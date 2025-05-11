from flask import Flask, render_template, request, jsonify
import datetime, retrieval, timeit
import sqlite3
from pathlib import Path
from collections import defaultdict
from flask_cors import CORS, cross_origin

connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

# Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
app.config['CORS_HEADERS'] = 'Content-Type'

# Get title, last modification date, size by page ID
def page_id_to_page_info(id: int) -> tuple[str, int, int]:
    page_info = cursor.execute("SELECT title, last_modification_date, size FROM pages WHERE page_id = ?", (id,)).fetchone()
    if page_info is None:
        raise ValueError("No page with the given ID is found.")
    return page_info

# Get URL by page ID
def page_id_to_url(id: int) -> str:
    url = cursor.execute("SELECT url FROM pages WHERE page_id = ?", (id,)).fetchone()
    if url is None:
        raise ValueError("No page with the given ID is found.")
    return url[0]

# Get top stems by page ID
def page_id_to_stems(id: int, num_stems: int = 5, include_title: bool = True) -> list[tuple[str, int]]:
    stems_freqs = list(cursor.execute("SELECT keyword_id, keyword_count FROM inverted_index WHERE page_id = ?", (id,)).fetchall())
    if include_title:
        stems_freqs += list(cursor.execute("SELECT keyword_id, keyword_count FROM title_inverted_index WHERE page_id = ?", (id,)).fetchall())
    if not stems_freqs:
        raise ValueError("No page with the given ID is found.")
    
    stems_ids = [stem[0] for stem in stems_freqs]
    freqs = [stem[1] for stem in stems_freqs]
    stems = [cursor.execute("SELECT keyword FROM keywords WHERE keyword_id = ?", (stem_id,)).fetchone()[0] for stem_id in stems_ids]
    stems_counts = list(zip(stems, freqs))
    d = defaultdict(int)
    for k, v in stems_counts:
        d[k] += v
    return sorted(d.items(), key=lambda x: x[1], reverse=True)[0:num_stems]

# Obtain parent or child links by page ID
def page_id_to_links(id: int, parent: bool = True) -> list[str]:
    link_ids = cursor.execute("SELECT parent_id FROM parent_child WHERE child_id = ?", (id,)).fetchall() if parent else cursor.execute("SELECT child_id FROM parent_child WHERE parent_id = ?", (id,)).fetchall()
    links = []
    for link_id in link_ids:
        try:
            links.append(page_id_to_url(link_id[0]))
        except ValueError:
            pass
    return links

# Convert a timestamp to a datetime string
def timestamp_to_datetime(timestamp: int):
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

# Class to represent a search result
class SearchResult:
    def __init__(self, id: int, score: float, num_keywords: int = 5):
        self.id = id
        self.score = score
        self.title, self.time, self.size = page_id_to_page_info(id)
        self.time_formatted = timestamp_to_datetime(self.time)
        self.url = page_id_to_url(id)
        self.keywords = page_id_to_stems(id, num_keywords)
        self.parent_links = page_id_to_links(id, parent=True)
        self.child_links = page_id_to_links(id, parent=False)

# Search page
@app.route("/")
def searchbar():
    return render_template("index.html")

# Handle search requests
@app.route("/search", methods=['POST'])
@cross_origin()
def submit_search():
    data = request.get_json()
    query = data.get('searchbar', "") if data else ""
    related_doc = data.get('related_doc', -1) if data else -1
    start_time = timeit.default_timer()
    search_results_raw = retrieval.search_engine(query, related_doc)
    search_time_taken = timeit.default_timer() - start_time

    filtered_results = [(ID, score) for ID, score in search_results_raw.items() if score != 0]
    
    # If no results, return early with an empty results array
    if not filtered_results:
        return jsonify({
            "query": query,
            "results": [],
            "time_taken": round(search_time_taken * 1000)
        })

    search_results = [SearchResult(ID, score) for ID, score in sorted(search_results_raw.items(), key = lambda x: x[1], reverse = True) if score != 0]
    
    response = jsonify({
        "query": query,
        "results": [
            {
                "id": result.id,
                "title": result.title,
                "url": result.url,
                "time": result.time_formatted,
                "size": result.size,
                "keywords": result.keywords,
                "parent_links": result.parent_links,
                "child_links": result.child_links,
                "score": round(result.score, 1),
            } for result in search_results
        ],
        "time_taken": round(search_time_taken * 1000)
    })
    return response


@app.route("/keywords", methods=['GET'])
@cross_origin()
def get_keywords():
    keywords = cursor.execute("SELECT keyword FROM keywords").fetchall()
    keywords = [keyword[0] for keyword in keywords]
    return jsonify(keywords)


# Flask
if __name__ == "__main__":
    app.run(debug = True)
