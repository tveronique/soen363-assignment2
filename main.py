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

# Fetch movie details from IMDBot API
def fetch_movie_details(imdb_id):
    url = f"https://search.imdbot.workers.dev/?tt={imdb_id}"
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
    return title, plot, viewers_rating, release_year, imdb_id

# Fetch Watchmode IDs using imdb_id obtained from IMDBot
def fetch_watchmode_movie_details(imdb_id):
    url = f"https://watchmode.p.rapidapi.com/search/?search_field=imdb_id&search_value={imdb_id}&types=movie"
    
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
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
        except Exception as e:
            print(f"Error inserting movie details: {e}")
            conn.rollback()

# Insert and fetch data for genre, keywords, contentRating, etc.
def insert_base_data():
    genres, contentRating, keywords, languages, country_names, country_ids, actors, directors = fetch_all_details()

    for genre in genres:
        insert_genre(genre)

    insert_contentRating(contentRating)

    insert_keywords(keywords)

    insert_languages(languages)

    insert_countries(country_names, country_ids)

    insert_actors(actors)

    insert_directors(directors)

    print("Base tables populated successfully.")

# Populate the movie table with related data
def populate_movie_with_related_data():
    # Movie ID you want to fetch (for example, "tt1099212" for Twilight part 2)
    imdb_id = "tt1099212"

    title, plot, viewers_rating, release_year, imdb_id = fetch_movie_details(imdb_id)
    if not imdb_id:
        print("IMDb ID not found, skipping Watchmode fetch.")
        return

    tmdb_id, watchmode_id = fetch_watchmode_movie_details(imdb_id)

    if title:
        insert_movie_details(title, plot, viewers_rating, release_year, imdb_id, tmdb_id, watchmode_id)

    print("Movie details inserted successfully.")

# Fetch data for genres, content ratings, keywords, languages, etc.
def fetch_all_details():
    genres = set() 
    contentRating = ""
    keywords = set()
    languages = set()
    country_names = []
    country_ids = []
    actors = set()
    directors = set()

    url = "https://search.imdbot.workers.dev/?tt=tt1099212"

    response = requests.get(url)
    
    print("Response Status Code:", response.status_code)
    try:
        json_response = response.json()
    except ValueError:
        print("Error: The response is not valid JSON.")
        return genres

    if response.status_code == 200:
        short_data = json_response.get("short", {})
        main_data = json_response.get("main", {})
        lang_data = main_data.get("spokenLanguages", {}).get("spokenLanguages", [])
        country_data = main_data.get("countriesOfOrigin", {}).get("countries", [])
        movie_genres = short_data.get("genre", [])
        movie_contentRating = short_data.get("contentRating")
        movie_keywords = short_data.get("keywords")  
        movie_languages = [lang.get("text") for lang in lang_data if lang.get("text")] 
        movie_country_names = [country.get("text") for country in country_data if country.get("text")] 
        movie_country_ids = [country.get("id") for country in country_data if country.get("id")]
        actors = short_data.get("actor", [])
        movie_actors = [act.get("name") for act in actors if act.get("name")]
        directors = short_data.get("director", [])
        movie_directors = [dir.get("name") for dir in directors if dir.get("name")]

        genres.update(movie_genres)
        contentRating = movie_contentRating if movie_contentRating else ""
        keywords.update(movie_keywords.split(","))
        languages.update(movie_languages)
        country_names = movie_country_names
        country_ids = movie_country_ids
        actors = movie_actors
        directors = movie_directors

    else:
        print(f"Error fetching data: {response.status_code}")

    return genres, contentRating, keywords, languages, country_names, country_ids, actors, directors

# Insert base data into respective tables
def insert_genre(name):
    with conn.cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO genre (name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING;
            """, (name,))
            conn.commit()
        except Exception as e:
            print(f"Error inserting genre {name}: {e}")

def insert_contentRating(content_rating):
    if content_rating:
        with conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO content_rating (rating)
                    VALUES (%s)
                    ON CONFLICT (rating) DO NOTHING;
                """, (content_rating,))
                conn.commit()
            except Exception as e:
                print(f"Error inserting content rating {content_rating}: {e}")

def insert_keywords(keywords):
    with conn.cursor() as cur:
        for keyword in keywords:
            try:
                cur.execute("""
                    INSERT INTO keyword (word)
                    VALUES (%s)
                    ON CONFLICT (word) DO NOTHING;
                """, (keyword,))
                conn.commit()
            except Exception as e:
                print(f"Error inserting keyword {keyword}: {e}")

def insert_languages(languages):
    with conn.cursor() as cur:
        for lang in languages:
            try:
                cur.execute("""
                    INSERT INTO language (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING;
                """, (lang,))
                conn.commit()
            except Exception as e:
                print(f"Error inserting language {lang}: {e}")

def insert_countries(country_names, country_ids):
    with conn.cursor() as cur:
        for name, country_id in zip(country_names, country_ids):
            try:
                cur.execute("""
                    INSERT INTO country (country_name, country_code)
                    VALUES (%s, %s)
                    ON CONFLICT (country_name) DO NOTHING;
               
