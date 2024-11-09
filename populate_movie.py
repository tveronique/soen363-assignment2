import requests
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# Connect to PostgreSQL database
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# This file fetches the details from IMDBot and WatchMode in order to populate the movie table 
# Info obtained from IMDBot: title, plot, viewer_rating, release_year, imdb_id
# Info obtained from WatchMode: tmdb_id, watchmode_id


# Fetch movie details from IMDBot API
def fetch_movie_details():
    url = "https://search.imdbot.workers.dev/?tt=tt1099212"  # for Twilight - part 2 & 3 movie
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error fetching IMDb data:", response.status_code)
        return None, None, None, None, None

    json_response = response.json()
    short_data = json_response.get("short", {})
    title = short_data.get("name")
    plot = short_data.get("description")
    rating = short_data.get("aggregateRating", {}).get("ratingValue")
    viewers_rating = float(rating) if rating else None
    release_year = int(short_data.get("datePublished", "")[:4]) if short_data.get("datePublished") else None
    imdb_id = json_response.get("imdbId")
    print(f"short data", imdb_id)
    return title, plot, viewers_rating, release_year, imdb_id

# Fetch Watchmode IDs using imdb_id obtained from IMDBot
def fetch_watchmode_movie_details(imdb_id):
    url = f"https://watchmode.p.rapidapi.com/search/?search_field=imdb_id&search_value={imdb_id}&types=movie"
    
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': 'watchmode.p.rapidapi.com'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching Watchmode data: {response.status_code}")
        return None, None

    json_response = response.json()
    title_results = json_response.get("title_results")

    if not title_results:
        print("No title results found in Watchmode for this IMDb ID.")
        return None, None

    tmdb_id = title_results[0].get("tmdb_id", None)
    watchmode_id = title_results[0].get("id", None)

    print("TMDB ID:", tmdb_id)
    print("Watchmode ID:", watchmode_id)
    
    return tmdb_id, watchmode_id

# Insert movie details into the database
def insert_movie_details(title, plot, viewers_rating, release_year, imdb_id, tmdb_id, watchmode_id):
    with conn.cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO movie (title, plot, viewers_rating, release_year, imdb_id, tmdb_id, watchmode_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (title, plot, viewers_rating, release_year, imdb_id, tmdb_id, watchmode_id))
            conn.commit()
            print("Movie details inserted successfully.")
        except Exception as e:
            print(f"Error inserting movie details: {e}")
            conn.rollback()

# Fetch and insert details from both APIs
def populate_all_details_from_apis():
    title, plot, viewers_rating, release_year, imdb_id = fetch_movie_details()
    
    if not imdb_id:
        print("IMDb ID not found, skipping Watchmode fetch.")
        return

    tmdb_id, watchmode_id = fetch_watchmode_movie_details(imdb_id)
    
    if title:
        insert_movie_details(title, plot, viewers_rating, release_year, imdb_id, tmdb_id, watchmode_id)

populate_all_details_from_apis()