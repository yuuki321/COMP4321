import math, sqlite3, re
from nltk.stem import PorterStemmer as Stemmer
from collections import Counter
from indexer import stem_words, remove_stop_words
from utils import encode_string

# Stemming
ps = Stemmer()
# Convert stopwords.txt to a list
stopwords = open('stopwords.txt', 'r').read().split()
connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

# Maximum number of search results
MAX_RESULTS = 50
# Global dictionaries to store processed data
Title_globalPageDict, Text_globalPageDict = {}, {} # {page_id: {word_id: TF-IDF score}}
globalWordtoID = {} # {word: word_id}
Title_globalPageStemText, Text_globalPageStemText = {}, {} # {page_id: stemmed text}
DOCUMENT_COUNT = cursor.execute("SELECT COUNT(page_id) FROM pages").fetchone()[0]

# Parse the query into single words and phrases
def parser(query: str) -> list[list[int]]:
    # Extract and stem single word
    keywords = [globalWordtoID[ps.stem(re.sub("[^a-zA-Z-]+", "", word.lower()))] for word in query.split()[:10000] if word.lower() not in stopwords and ps.stem(re.sub("[^a-zA-Z-]+", "", word.lower())) in globalWordtoID]
    # Extract and stem phrases
    phrases_no_stopword = [r"(?<!\S){}(?!\S)".format(" ".join(ps.stem(word) for word in phrase.lower().split() if word not in stopwords)) for phrase in re.findall('"([^"]*)"', query) if phrase]
    keywords += [encode_string(' '.join(stem_words(remove_stop_words(phrase.split())))) for phrase in re.findall('"([^"]*)"', query) if phrase]
    return [keywords, phrases_no_stopword]

# Convert a query in a vector
def queryToVec(queryEncoding: list[int]) -> dict[int, int]: return Counter(queryEncoding) if queryEncoding else {}

# Convert a document to a TF-IDF vector
def documentToVec(page_id: int, fromTitle: bool = False) -> dict[int, int]:
    table = "title_inverted_index" if fromTitle else "inverted_index"
    # Use title_inverted_index or inverted_index based on the flag
    wordList = cursor.execute(f"SELECT keyword_id, keyword_count FROM {table} WHERE page_id = ?", (page_id,)).fetchall()
    # Calculate max term frequency (TF)
    maxTF = cursor.execute(f"SELECT MAX(keyword_count) FROM {table} WHERE page_id = ?", (page_id,)).fetchone()[0]
    forwardIdx = "title_forward_index" if fromTitle else "forward_index"
    # Use title_forward_index or forward_index based on the flag
    word_counts = {word_id: count for word_id, count in cursor.execute(f"SELECT keyword_id, keyword_count FROM {forwardIdx} WHERE keyword_id IN ({','.join('?' for _ in wordList)})", [word for word, _ in wordList]).fetchall()}
    # Calculate TF-IDF scores for each word
    return {word: tf * math.log2(DOCUMENT_COUNT / word_counts[word]) / maxTF for word, tf in wordList} if wordList else {}

# Calculate cosine similarity between two vectors
# vector 1: query vector
# vector 2: document vector
def cosinesimilarity(vector1: dict[int, int, int], vector2: dict[int, int, int]) -> float:
    commonwords = set(vector1.keys()) & set(vector2.keys())
    if not commonwords: return 0.0
    # Normalize vectors
    def normalize(vector):
        magnitude = math.sqrt(sum(value**2 for value in vector.values()))
        return {word: value / magnitude for word, value in vector.items()} if magnitude != 0 else vector
    # Dot product of two normalized vectors
    vector1n = normalize(vector1)
    vector2n = normalize(vector2)
    dot_product = sum(vector1n[word] * vector2n[word] for word in commonwords)
    score = dot_product * 50
    return score

# Filter documents based on phrases
def phraseFilter(document_id: int, phrases: list[str]) -> bool:
    return all(re.search(phrase, Title_globalPageStemText[document_id]) or re.search(phrase, Text_globalPageStemText[document_id]) for phrase in phrases) if phrases else True

# Filter documents based on query words
def queryFilter(document_id: int, query: list[int]) -> bool:
    return any(word in Title_globalPageDict[document_id] or word in Text_globalPageDict[document_id] for word in query) if query else True

# Start searching
def search_engine(query: str, related_doc: int = -1) -> dict[int, float]:
    """ Returns a dictionary containing the search results. A related document can be optinally specified to improve the search results.

    Args:
        query (str): The search query.
        related_doc (int, optional): The ID of a related document to improve the search results. Defaults to -1.
    """
    if not query: return {}
    splitted_query = parser(query)
    vector1 = queryToVec(splitted_query[0])

    # Query modification
    if related_doc != -1:
        related_doc = cursor.execute("SELECT page_id FROM pages WHERE page_id = ?", (related_doc,)).fetchone()
        if not related_doc: return {}
        related_doc = related_doc[0]
        document_vec = documentToVec(related_doc)
        document_vec = {word: score / 2 for word, score in document_vec.items()}
        vector1 = {word: score + document_vec.get(word, 0) for word, score in vector1.items()}
        
    if not splitted_query[0]: return {}
    title_cosinescores, text_cosinescores = {}, {}
    for document in allDocs:
        document = document[0]
        if splitted_query[1] and not phraseFilter(document, splitted_query[1]): continue
        if not queryFilter(document, splitted_query[0]): continue
        title_vector2, text_vector2 = Title_globalPageDict[document], Text_globalPageDict[document]
        title_cosinescores[document] = cosinesimilarity(vector1, title_vector2)
        text_cosinescores[document] = cosinesimilarity(vector1, text_vector2)
    # Normalize scores
    def normalize_scores(scores: dict[int, float]) -> dict[int, float]:
        max_score = max(scores.values(), default=1)
        return {key: (value / max_score) * 50 for key, value in scores.items()} if max_score != 0 else scores
    title_cosinescores = normalize_scores(title_cosinescores)
    text_cosinescores = normalize_scores(text_cosinescores)
    # Sort and limit results
    title_cosinescores = dict(sorted(title_cosinescores.items(), key=lambda item: item[1], reverse=True)[:MAX_RESULTS])
    text_cosinescores = dict(sorted(text_cosinescores.items(), key=lambda item: item[1], reverse=True)[:MAX_RESULTS])
    # Combine title and text scores with weights
    combined_Scores = {key: 0.3 * title_cosinescores.get(key, 0) + 0.7 * text_cosinescores.get(key, 0) for key in set(title_cosinescores) | set(text_cosinescores)}
    # Calculate ranking scores
    RankingScore = {page_id: score for page_id, score in cursor.execute(f"SELECT page_id, score FROM page_ranks WHERE page_id IN ({','.join('?' for _ in combined_Scores)})", tuple(combined_Scores.keys())).fetchall()}
    combined_Scores = {page_id: score * RankingScore.get(page_id, 0) for page_id, score in combined_Scores.items()}
    scores = normalize_scores(combined_Scores)
    return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True)[:MAX_RESULTS])

# Populate global dictionaries
allDocs = cursor.execute("SELECT page_id FROM pages").fetchall()
for doc in allDocs:
    doc = doc[0]
    Title_globalPageDict[doc] = documentToVec(doc, True)
    Text_globalPageDict[doc] = documentToVec(doc)
    Title_globalPageStemText[doc] = ' '.join(stem_words(remove_stop_words(cursor.execute("SELECT clean_title FROM pages WHERE page_id = ?", (doc,)).fetchone()[0].split())))
    Text_globalPageStemText[doc] = ' '.join(stem_words(remove_stop_words(cursor.execute("SELECT clean_body FROM pages WHERE page_id = ?", (doc,)).fetchone()[0].split())))
globalWordtoID = {word: word_id for word_id, word in cursor.execute("SELECT keyword_id, keyword FROM keywords").fetchall()}