import requests
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

#This file fetches the details from IMDBot for the tables that have no foreign keys i.e. for genre, content rating, keyword, language, country, actor, director
def fetch_all_details():
    genres = set() 
    contentRating = ""
    keywords = set()
    languages = set()
    country_name = ""
    country_id = ""
    actors = set()
    directors = set()

    url = "https://search.imdbot.workers.dev/?tt=tt1099212"  # for Twilight - part 2 & 3 movie

    # GET request to the API
    response = requests.get(url)
    
    # Status code -- success is 200
    print("Response Status Code:", response.status_code)
    try:
        json_response = response.json()  # Parse JSON response
        # print("Response JSON:", json_response)  # Print the JSON response to see the structure
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
        movie_country_name = [country.get("text") for country in country_data if country.get("text")] 
        movie_country_id = [country.get("id") for country in country_data if country.get("id")]
        actors = short_data.get("actor", [])
        movie_actors = [act.get("name") for act in actors if act.get("name")]
        directors = short_data.get("director", [])
        movie_directors = [dir.get("name") for dir in directors if dir.get("name")]

        if isinstance(movie_genres, list):
            genres.update(movie_genres)

        if movie_contentRating:
            contentRating = movie_contentRating

        if movie_keywords:
            keywords.update(movie_keywords.split(","))

        if movie_languages:
            languages.update(movie_languages)

        if movie_country_name:
            country_name = movie_country_name

        if movie_country_id:
            country_id = movie_country_id

        if movie_actors:
            actors = movie_actors

        if movie_directors:
            directors = movie_directors

    else:
        print(f"Error fetching data: {response.status_code}")

    return genres, contentRating, keywords, languages, country_name, country_id, actors, directors

# Functions to insert details into their tables if they don't already exist
def insert_genre(name):
    with conn.cursor() as cur:
        try:
            cur.execute("SELECT 1 FROM genre WHERE name = %s", (name,))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO genre (name) VALUES (%s)", (name,))
                conn.commit()
        except Exception as e:
            print(f"Error inserting genre {name}: {e}")

def insert_contentRating(content_rating):
    if content_rating:
        with conn.cursor() as cur:
            try:
                cur.execute("SELECT 1 FROM content_rating WHERE rating = %s", (content_rating,))
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO content_rating (rating) VALUES (%s)", (content_rating,))
                    conn.commit()
            except Exception as e:
                print(f"Error inserting content rating {content_rating}: {e}")

def insert_keywords(keywords):
    with conn.cursor() as cur:
        for keyword in keywords:
            try:
                cur.execute("SELECT 1 FROM keyword WHERE word = %s", (keyword,))
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO keyword (word) VALUES (%s)", (keyword,))
                    conn.commit()
            except Exception as e:
                print(f"Error inserting keyword {keyword}: {e}")

def insert_languages(languages):
    with conn.cursor() as cur:
        for lang in languages:
            try:
                cur.execute("SELECT 1 FROM language WHERE name = %s", (lang,))
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO language (name) VALUES (%s)", (lang,))
                    conn.commit()
            except Exception as e:
                print(f"Error inserting language {lang}: {e}")

def insert_countries(country_names, country_ids):
    with conn.cursor() as cur:
        for name, country_id in zip(country_names, country_ids):
            try:
                cur.execute("SELECT 1 FROM country WHERE country_name = %s", (name,))
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO country (country_name, country_code) VALUES (%s, %s)", (name, country_id))
                    conn.commit()
            except Exception as e:
                print(f"Error inserting country {name} with ID {country_id}: {e}")

def insert_actors(actors):
    with conn.cursor() as cur:
        for act in actors:
            try:
                cur.execute("SELECT 1 FROM actor WHERE name = %s", (act,))
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO actor (name) VALUES (%s)", (act,))
                    conn.commit()
            except Exception as e:
                print(f"Error inserting actor {act}: {e}")

def insert_directors(directors):
    with conn.cursor() as cur:
        for dir in directors:
            try:
                cur.execute("SELECT 1 FROM director WHERE name = %s", (dir,))
                if cur.fetchone() is None:
                    cur.execute("INSERT INTO director (name) VALUES (%s)", (dir,))
                    conn.commit()
            except Exception as e:
                print(f"Error inserting director {dir}: {e}")

# Main function to populate the base tables
def populate_all_details_from_api():
    genres, contentRating, keywords, languages, country_name, country_id, actors, directors = fetch_all_details()

    for genre in genres:
        insert_genre(genre)

    insert_contentRating(contentRating)

    insert_keywords(keywords)

    insert_languages(languages)

    insert_countries(country_name, country_id)

    insert_actors(actors)

    insert_directors(directors)

    print("All tables populated successfully.")

populate_all_details_from_api()
