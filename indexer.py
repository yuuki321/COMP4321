from nltk.stem import PorterStemmer as Stemmer
import numpy as np
import sqlite3
from utils import encode_string
from collections import Counter
import spacy

ps = Stemmer()
stopwords = open('stopwords.txt', 'r').read().split()


def stem_words(words: list[str]) -> list[str]:
    """Stems the words using the Porter Stemmer algorithm."""
    return [ps.stem(word) for word in words]


def remove_stop_words(words: list[str]) -> list[str]:
    """Removes stopwords from the list of words."""
    return [word for word in words if word not in stopwords]


def generate_adjacency_matrix(all_pages: list[int]) -> np.ndarray:
    """Generates an adjacency matrix from the list of all pages.
    
    Args:
        all_pages (list[int]): List of all page IDs.
    """
    matrixMap = {key: {val: 0 for val in all_pages} for key in all_pages}
    for page in all_pages:
        children = cursor.execute(f'SELECT child_id FROM parent_child WHERE parent_id = {page}').fetchall()
        for child in children:
            matrixMap[page][child[0]] = 1
    return np.array([[val for val in matrixMap[key].values()] for key in matrixMap.keys()]).T


def insert_single_keywords(cursor) -> None:
    """Inserts single keywords into the database."""
    all_pages = cursor.execute('SELECT page_id FROM pages').fetchall()
    body_keywords = {} # Word ID -> Frequency
    title_keywords = {} # Word ID -> Frequency
    for page in all_pages:
        body, title = cursor.execute(f'SELECT clean_body, clean_title FROM pages WHERE page_id = {page[0]}').fetchone()
        body = stem_words(remove_stop_words(body.split()))
        title = stem_words(remove_stop_words(title.split()))
        for word in body:
            word_id = encode_string(word)
            if word_id not in body_keywords:
                body_keywords[word_id] = 1
            else:
                body_keywords[word_id] += 1
        for word in title:
            word_id = encode_string(word)
            if word_id not in title_keywords:
                title_keywords[word_id] = 1
            else:
                title_keywords[word_id] += 1
        all_words = set(body + title)
        for word in all_words:
            cursor.execute(f'''
                INSERT OR IGNORE INTO keywords (keyword_id, keyword)
                VALUES ({encode_string(word)}, '{word}');
            ''')
        for word, count in Counter(body).items():
            cursor.execute(f'''
                INSERT INTO inverted_index (page_id, keyword_id, keyword_count)
                VALUES ({page[0]}, {encode_string(word)}, {count});
            ''')
        for word, count in Counter(title).items():
            cursor.execute(f'''
                INSERT INTO title_inverted_index (page_id, keyword_id, keyword_count)
                VALUES ({page[0]}, {encode_string(word)}, {count});
            ''')
    for word_id, count in body_keywords.items():
        cursor.execute(f'''
            INSERT INTO forward_index (keyword_id, keyword_count)
            VALUES ({word_id}, {count});
        ''')
    for word_id, count in title_keywords.items():
        cursor.execute(f'''
            INSERT INTO title_forward_index (keyword_id, keyword_count)
            VALUES ({word_id}, {count});
        ''')
    
    connection.commit()


def insert_phrase_keywords(cursor) -> None:
    """Inserts phrase keywords into the database using spaCy."""
    all_pages = cursor.execute('SELECT page_id FROM pages').fetchall()
    # Dictionaries to track phrase occurrences across all documents
    body_phrases = {}  # Word ID -> Frequency
    title_phrases = {}  # Word ID -> Frequency
    
    # Get all words from the documents including the bodies and titles
    text = ''
    for page in all_pages:
        body, title = cursor.execute('SELECT clean_body, clean_title FROM pages WHERE page_id = ?', (page[0],)).fetchone()
        text += ' '.join(remove_stop_words((body + ' ' + title + ' ').split()))
    
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    all_phrases = [' '.join(stem_words(ent.text.split())) for ent in doc.ents if len(ent.text.split()) > 1 and len(ent.text.split()) <= 3]
    
    # Insert all phrases into keywords table
    for phrase in all_phrases:
        word_id = encode_string(phrase)
        cursor.execute('''
            INSERT OR IGNORE INTO keywords (keyword_id, keyword)
            VALUES (?, ?);
        ''', (word_id, phrase))
    
    # Process each page for inverted indices
    for page in all_pages:
        page_id = page[0]
        body, title = cursor.execute('SELECT clean_body, clean_title FROM pages WHERE page_id = ?', (page_id,)).fetchone()
        
        # Process body text for phrases
        body_doc = nlp(body)
        body_phrases_in_page = [' '.join(stem_words(ent.text.split())) for ent in body_doc.ents if len(ent.text.split()) > 1 and len(ent.text.split()) <= 3]
        body_phrase_counts = Counter(body_phrases_in_page)
        
        # Process title text for phrases
        title_doc = nlp(title)
        title_phrases_in_page = [' '.join(stem_words(ent.text.split())) for ent in title_doc.ents if len(ent.text.split()) > 1 and len(ent.text.split()) <= 3]
        title_phrase_counts = Counter(title_phrases_in_page)
        
        # Update global phrase counts and insert into inverted indices
        for phrase, count in body_phrase_counts.items():
            word_id = encode_string(phrase)
            
            # First ensure the keyword exists in the keywords table
            cursor.execute('''
                INSERT OR IGNORE INTO keywords (keyword_id, keyword)
                VALUES (?, ?);
            ''', (word_id, phrase))
            
            # Update phrase counts
            if word_id not in body_phrases:
                body_phrases[word_id] = count
            else:
                body_phrases[word_id] += count
            
            # Insert into inverted index using the same word_id
            cursor.execute('''
                INSERT OR IGNORE INTO inverted_index (page_id, keyword_id, keyword_count)
                VALUES (?, ?, ?);
            ''', (page_id, word_id, count))
        
        for phrase, count in title_phrase_counts.items():
            word_id = encode_string(phrase)
            
            # First ensure the keyword exists in the keywords table
            cursor.execute('''
                INSERT OR IGNORE INTO keywords (keyword_id, keyword)
                VALUES (?, ?);
            ''', (word_id, phrase))
            
            # Update phrase counts
            if word_id not in title_phrases:
                title_phrases[word_id] = count
            else:
                title_phrases[word_id] += count
            
            # Insert into title inverted index using the same word_id
            cursor.execute('''
                INSERT OR IGNORE INTO title_inverted_index (page_id, keyword_id, keyword_count)
                VALUES (?, ?, ?);
            ''', (page_id, word_id, count))
    
    # Insert into forward indices
    for word_id, count in body_phrases.items():
        cursor.execute('''
            INSERT OR IGNORE INTO forward_index (keyword_id, keyword_count)
            VALUES (?, ?);
        ''', (word_id, count))
    
    for word_id, count in title_phrases.items():
        cursor.execute('''
            INSERT OR IGNORE INTO title_forward_index (keyword_id, keyword_count)
            VALUES (?, ?);
        ''', (word_id, count))
    
    connection.commit()


def ranks (current_ranking_score: np.ndarray, adjacency_matrix: np.ndarray, teleportation_probability: float, max_iterations: int = 100) -> np.ndarray:
    """Calculates the PageRank scores for each page."""
    ranking_scores = current_ranking_score
    # Update ranking scores based on the adjacency matrix
    for _ in range(max_iterations):
        new_ranking_scores = adjacency_matrix.dot(ranking_scores)
        # Apply teleportation probability to the new scores
        new_ranking_scores = teleportation_probability + (1 - teleportation_probability) * new_ranking_scores
        # Stop iteration after the scores converge
        if np.allclose(ranking_scores, new_ranking_scores):
            break
        ranking_scores = new_ranking_scores
    return ranking_scores

def insert_page_ranks(cursor) -> None:
    """Inserts page ranks into the database."""
    all_pages = cursor.execute('SELECT page_id FROM pages').fetchall()
    adjacency_matrix = generate_adjacency_matrix([page[0] for page in all_pages])
    ranking_scores = ranks(np.ones(len(all_pages)), adjacency_matrix, 0.85)
    for page_id, score in zip([page[0] for page in all_pages], ranking_scores):
        cursor.execute('''
            INSERT OR IGNORE INTO page_ranks (page_id, score)
            VALUES (?, ?);
        ''', (page_id, score))
    connection.commit()


if __name__ == '__main__':
    DATABASE_PATH = 'database.db'
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    insert_single_keywords(cursor)
    insert_phrase_keywords(cursor)
    insert_page_ranks(cursor)
    connection.close()