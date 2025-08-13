### COMP4321 Project -  Search Engine System
For the project report, please click [here](https://github.com/yuuki321/COMP4321/blob/main/COMP4321%20Final%20Project%20Report.pdf).

## Run

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the environment by running the activate script:

   On Windows:
   ```bash
   venv\Scripts\activate
   ```

   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

3. Install the libraries in the virtual environment.

4. To build the database, run these lines:
   ```bash
   python spider.py
   python indexer.py
   ```

5. Run the app:
   ```bash
   python app.py
   ```

6. Set up the frontend by running:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

7. Open the app at:
   ```
   http://localhost:5173
   ```
