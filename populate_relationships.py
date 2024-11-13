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

# This file fetches the details from IMDBot and the movie id to compare the associations and add them to their corresponding relationship with movie 
# This file also populates the movie_aka table which is a weak relationship between movie and aka (movie is the strong entity)

imdb_api_url = 'https://search.imdbot.workers.dev/?tt=tt1099212'

try:
    response = requests.get(imdb_api_url)
    response.raise_for_status()

    short_data = response.json().get("short", {})
    main_data = response.json().get("main", {})
    imdb_id = response.json().get("imdbId", None)

    with conn.cursor() as cur:
        movie_query = 'SELECT id FROM movie WHERE imdb_id = %s LIMIT 1'
        cur.execute(movie_query, (imdb_id,))
        movie_result = cur.fetchone()
        
        if movie_result is None:
            print(f"Movie with IMDb ID {imdb_id} not found in the database.")
        else:
            movie_id = movie_result[0]
            genres = short_data.get("genre", [])
            country_data = main_data.get("countriesOfOrigin", {}).get("countries", [])
            countries = [country.get("text") for country in country_data if country.get("text")]
            movie_actors = short_data.get("actor", [])
            actors = [act.get("name") for act in movie_actors if act.get("name")]
            movie_directors = short_data.get("director", [])
            directors = [dir.get("name") for dir in movie_directors if dir.get("name")]
            keywords = set(short_data.get("keywords", "").split(","))
            lang_data = main_data.get("spokenLanguages", {}).get("spokenLanguages", [])
            languages = [lang.get("text") for lang in lang_data if lang.get("text")] 
            content_rating = short_data.get("contentRating", None)
            akas_data = main_data.get("akas", {}).get("edges", [])
            akas = [aka.get("node", {}).get("text") for aka in akas_data if aka.get("node", {}).get("text")]

            for aka_title in akas:
                cur.execute(
                    '''
                    SELECT 1 FROM movie_aka WHERE aka_title = %s AND movie_id = %s LIMIT 1
                    ''', (aka_title, movie_id)
                )
                if not cur.fetchone():
                    cur.execute(
                        '''
                        INSERT INTO movie_aka (aka_title, movie_id)
                        VALUES (%s, %s) ON CONFLICT (aka_title, movie_id) DO NOTHING;
                        ''', (aka_title, movie_id)
                    )

            for genre_name in genres:
                genre_query = 'SELECT id FROM genre WHERE name = %s LIMIT 1'
                cur.execute(genre_query, (genre_name,))
                genre_result = cur.fetchone()
                if genre_result:
                    genre_id = genre_result[0]
                    cur.execute(
                        '''
                        SELECT 1 FROM movie_genre WHERE movie_id = %s AND genre_id = %s LIMIT 1
                        ''', (movie_id, genre_id)
                    )
                    if not cur.fetchone():
                        cur.execute(
                            '''
                            INSERT INTO movie_genre (movie_id, genre_id)
                            VALUES (%s, %s) ON CONFLICT DO NOTHING;
                            ''', (movie_id, genre_id)
                        )

            for country_name in countries:
                country_query = 'SELECT country_id FROM country WHERE country_name = %s LIMIT 1'
                cur.execute(country_query, (country_name,))
                country_result = cur.fetchone()
                if country_result:
                    country_id = country_result[0]
                    cur.execute(
                        '''
                        SELECT 1 FROM movie_country WHERE movie_id = %s AND country_id = %s LIMIT 1
                        ''', (movie_id, country_id)
                    )
                    if not cur.fetchone():
                        cur.execute(
                            '''
                            INSERT INTO movie_country (movie_id, country_id)
                            VALUES (%s, %s) ON CONFLICT DO NOTHING;
                            ''', (movie_id, country_id)
                        )

            for actor_name in actors:
                actor_query = 'SELECT id FROM actor WHERE name = %s LIMIT 1'
                cur.execute(actor_query, (actor_name,))
                actor_result = cur.fetchone()
                if actor_result:
                    actor_id = actor_result[0]
                    cur.execute(
                        '''
                        SELECT 1 FROM movie_actor WHERE movie_id = %s AND actor_id = %s LIMIT 1
                        ''', (movie_id, actor_id)
                    )
                    if not cur.fetchone():
                        cur.execute(
                            '''
                            INSERT INTO movie_actor (movie_id, actor_id)
                            VALUES (%s, %s) ON CONFLICT DO NOTHING;
                            ''', (movie_id, actor_id)
                        )

            for director_name in directors:
                director_query = 'SELECT id FROM director WHERE name = %s LIMIT 1'
                cur.execute(director_query, (director_name,))
                director_result = cur.fetchone()
                if director_result:
                    director_id = director_result[0]
                    cur.execute(
                        '''
                        SELECT 1 FROM movie_director WHERE movie_id = %s AND director_id = %s LIMIT 1
                        ''', (movie_id, director_id)
                    )
                    if not cur.fetchone():
                        cur.execute(
                            '''
                            INSERT INTO movie_director (movie_id, director_id)
                            VALUES (%s, %s) ON CONFLICT DO NOTHING;
                            ''', (movie_id, director_id)
                        )

            for keyword in keywords:
                keyword_query = 'SELECT id FROM keyword WHERE word = %s LIMIT 1'
                cur.execute(keyword_query, (keyword,))
                keyword_result = cur.fetchone()
                if keyword_result:
                    keyword_id = keyword_result[0]
                    cur.execute(
                        '''
                        SELECT 1 FROM movie_keyword WHERE movie_id = %s AND keyword_id = %s LIMIT 1
                        ''', (movie_id, keyword_id)
                    )
                    if not cur.fetchone():
                        cur.execute(
                            '''
                            INSERT INTO movie_keyword (movie_id, keyword_id)
                            VALUES (%s, %s) ON CONFLICT DO NOTHING;
                            ''', (movie_id, keyword_id)
                        )

            for language_name in languages:
                language_query = 'SELECT id FROM language WHERE name = %s LIMIT 1'
                cur.execute(language_query, (language_name,))
                language_result = cur.fetchone()
                if language_result:
                    language_id = language_result[0]
                    cur.execute(
                        '''
                        SELECT 1 FROM movie_language WHERE movie_id = %s AND language_id = %s LIMIT 1
                        ''', (movie_id, language_id)
                    )
                    if not cur.fetchone():
                        cur.execute(
                            '''
                            INSERT INTO movie_language (movie_id, language_id)
                            VALUES (%s, %s) ON CONFLICT DO NOTHING;
                            ''', (movie_id, language_id)
                        )

            if content_rating:
                content_rating_query = 'SELECT id FROM content_rating WHERE rating = %s LIMIT 1'
                cur.execute(content_rating_query, (content_rating,))
                content_rating_result = cur.fetchone()
                if content_rating_result:
                    content_rating_id = content_rating_result[0]
                    cur.execute(
                        '''
                        SELECT 1 FROM movie_contentrating WHERE movie_id = %s AND content_rating_id = %s LIMIT 1
                        ''', (movie_id, content_rating_id)
                    )
                    if not cur.fetchone():
                        cur.execute(
                            '''
                            INSERT INTO movie_contentrating (movie_id, content_rating_id)
                            VALUES (%s, %s) ON CONFLICT DO NOTHING;
                            ''', (movie_id, content_rating_id)
                        )

            conn.commit()
            print("All relationships processed and committed.")

except requests.exceptions.RequestException as error:
    print(f"Error fetching data from IMDb API: {error}")

finally:
    conn.close()
    print("Database connection closed.")