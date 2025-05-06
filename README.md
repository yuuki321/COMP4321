Run

```
python -m venv venv
```

and activate the environment by running the activate script.

Install the libraries in venv.

The database can be deleted. To build the database, run these lines:

```
python spider.py
python indexer.py
```

Run the app by running

```
python app.py
```

**What I have done**

- Reorganized the tables, removed redundant ones and renamed entities
- Added documentation to spider and indexer. I couldn't do that for retrieval because I couldn't figure out all functions
- Added `utils.py`, planning to move all helper functions in `app.py` to utils for better access and management. APIs and helpers should be in 2 files
- Added phrases. They should be present in the db and are searchable through the app
