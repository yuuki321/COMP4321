from bs4 import BeautifulSoup as bsoup
import requests
from email.utils import parsedate_to_datetime
from datetime import datetime
from urllib.parse import urljoin, urlparse
from utils import encode_string
import sqlite3
import re


def parse_html(url: str) -> tuple:
    """Returns the BeautifulSoup object, last modification date, and size of the page.
    Returns empty content if an error is encountered.

    Returns:
        soup (BeautifulSoup): The parsed HTML content of the page.
        last_modification_date (int): The last modification date of the page as a timestamp.
        size (int): The size of the page in bytes.
    """
    if not url.startswith(('https://', 'http://')):
        url = 'https://' + url
    try:
        request = requests.get(url, verify=False, timeout=30)
        soup = bsoup(request.text, "lxml")
        last_modification_date = int(datetime.timestamp(parsedate_to_datetime(request.headers.get("last-modified", request.headers["Date"]))))
        size = int(request.headers.get("content-length", len(request.content)))
        return soup, last_modification_date, size
    except Exception as e:
        print(f"Error: {str(e)}")
        return tuple()


def normalize_url(url: str) -> str:
    """Normalizes the URL."""
    return f"{urlparse(url).scheme}://{urlparse(url).netloc}{urlparse(url).path}"


def get_child_links(url: str, soup: bsoup) -> list[str]:
    """Returns a list of normalized links present on a page."""
    if not soup:
        return []
    return [f"{urlparse(urljoin(url, anchor['href'])).scheme}://{urlparse(urljoin(url, anchor['href'])).netloc}{urlparse(urljoin(url, anchor['href'])).path}".rstrip("/") for anchor in soup.findAll("a", href=True)]


def get_information(current_url: str, soup: bsoup):
    """Extracts information from a page and returns the terms.

    Returns:
        current_page_id (int): The ID of the current page computed with CRC32.
        title (str): The title of the page.
        clean_body (str): The body of the page.
        clean_title (str): The cleaned title of the page.
        normalized_url (str): The normalized URL of the page.
    """
    if not soup:
        return None, None, None, None

    title = soup.title.string if soup.title else "No Title"
    normalized_url = normalize_url(current_url)
    current_page_id = encode_string(normalized_url)
    clean_title = ' '.join([re.sub("[^a-zA-Z-]+", " ", word).lower() for word in title.split() if word])
    clean_body = ' '.join([re.sub("[^a-zA-Z-]+", " ", word).lower() for word in soup.get_text(separator="\n").split() if word])
    return current_page_id, title, clean_body, clean_title, normalized_url


def init_db() -> None:
    """Initializes the database."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            keyword_id INTEGER PRIMARY KEY,
            keyword TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            page_id INTEGER PRIMARY KEY,
            size INTEGER NOT NULL,
            last_modification_date INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            clean_body TEXT NOT NULL,
            clean_title TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forward_index (
            keyword_id INTEGER NOT NULL,
            keyword_count INTEGER NOT NULL,
            FOREIGN KEY (keyword_id) REFERENCES keywords (keyword_id) ON DELETE CASCADE    
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inverted_index (
            page_id INTEGER NOT NULL,
            keyword_id INTEGER NOT NULL,
            keyword_count INTEGER NOT NULL,
            FOREIGN KEY (page_id) REFERENCES pages (page_id) ON DELETE CASCADE,
            FOREIGN KEY (keyword_id) REFERENCES keywords (keyword_id) ON DELETE CASCADE
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS title_forward_index (
            keyword_id INTEGER NOT NULL,
            keyword_count INTEGER NOT NULL,
            FOREIGN KEY (keyword_id) REFERENCES keywords (keyword_id) ON DELETE CASCADE    
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS title_inverted_index (
            page_id INTEGER NOT NULL,
            keyword_id INTEGER NOT NULL,
            keyword_count INTEGER NOT NULL,
            FOREIGN KEY (page_id) REFERENCES pages (page_id) ON DELETE CASCADE,
            FOREIGN KEY (keyword_id) REFERENCES keywords (keyword_id) ON DELETE CASCADE
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parent_child (
            parent_id INTEGER NOT NULL,
            child_id INTEGER NOT NULL,
            FOREIGN KEY (parent_id) REFERENCES pages (page_id) ON DELETE CASCADE,
            FOREIGN KEY (child_id) REFERENCES pages (page_id) ON DELETE CASCADE
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS page_ranks (
            page_id INTEGER PRIMARY KEY,
            score INTEGER NOT NULL,
            FOREIGN KEY (page_id) REFERENCES pages (page_id) ON DELETE CASCADE           
        );
    """)
    connection.commit()


def recursively_crawl(url: str) -> None:
    """Recursively crawls the requested page and all its child pages in a breadth-first search manner."""
    queue = [url]
    visited = set()
    parent_child = [] # Stores the parent-child relations that will be inserted into the database

    while len(queue) > 0:
        current_url = queue.pop(0)
        soup, last_modification_date, size = parse_html(current_url)
        if cursor.execute(f'SELECT COUNT(*) FROM pages WHERE url = "{current_url}"').fetchone()[0] > 0:
            cursor.execute(f'SELECT last_modification_date FROM pages WHERE url = "{current_url}"')
            # Skip if the page has not been modified since the last crawl
            if cursor.fetchone()[0] >= last_modification_date:
                continue
            else:
                cursor.execute(f'DELETE FROM pages WHERE url = "{current_url}"')
                connection.commit()
        
        visited.add(current_url)
        child_links = get_child_links(current_url, soup)
        current_page_id, title, clean_body, clean_title, normalized_url = get_information(current_url, soup)

        cursor.execute(f'''
            INSERT INTO pages (page_id, size, last_modification_date, title, url, clean_body, clean_title)
            VALUES ({current_page_id}, {size}, {last_modification_date}, "{title}", "{normalized_url}", "{clean_body}", "{clean_title}");
        ''')
        connection.commit()

        for child_link in child_links:
            child_page_id = encode_string(normalize_url(child_link))
            parent_child.append({
                "parent_id": current_page_id,
                "child_id": child_page_id
            })
            if child_link not in visited and child_link not in queue:
                queue.append(child_link)

    for relation in parent_child:
        parent_id = relation["parent_id"]
        child_id = relation["child_id"]
        cursor.execute(f"""
            INSERT INTO parent_child (parent_id, child_id)
            VALUES ({parent_id}, {child_id});
        """)
    connection.commit()


if __name__ == "__main__":
    DATABASE_PATH = 'database.db'
    START_URL = 'https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm'
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    init_db()
    recursively_crawl(START_URL)
    connection.close()