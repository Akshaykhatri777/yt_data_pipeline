--YouTube Trending Data Pipeline

Fetches trending YouTube videos using the YouTube Data API, cleans the data with Pandas, and loads it into PostgreSQL for analysis.

--Tech Stack
- Python (requests, pandas, sqlalchemy)
- PostgreSQL
- YouTube Data API v3

## How to Run
1. Clone this repo
2. Create virtual environment & activate
    ```bash
    python -m venv venv
    venv\Scripts\activate  # on Windows
    ```
3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
4. Create a `.env` file (copy `.env.example`), fill in your API & DB info
5. Run the pipeline
    ```bash
    python fetch_trending.py
    ```
