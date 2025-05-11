Run

```
python -m venv venv
```

and activate the environment by running the activate script:

On Windows:

```
venv\Scripts\activate
```

On macOS/Linux:

```
source .venv/bin/activate
```

Install the libraries in venv.

To build the database, run these lines:

```
python spider.py
python indexer.py
```

Run the app by running

```
python app.py
```

Set up the frontend by running

```
cd frontend
npm install
npm run dev
```

And open the app at localhost:5173
