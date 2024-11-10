# relationships.py

import psycopg2
from psycopg2 import sql

def insert_movie_director(connection, movie_id, director_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO movie_director (movie_id, director_id)
            VALUES (%s, %s);
            """,
            (movie_id, director_id)
        )
    connection.commit()

def insert_movie_genre(connection, movie_id, genre_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO movie_genre (movie_id, genre_id)
            VALUES (%s, %s);
            """,
            (movie_id, genre_id)
        )
    connection.commit()

def insert_movie_language(connection, movie_id, language_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO movie_language (movie_id, language_id)
            VALUES (%s, %s);
            """,
            (movie_id, language_id)
        )
    connection.commit()

def insert_movie_keyword(connection, movie_id, keyword_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO movie_keyword (movie_id, keyword_id)
            VALUES (%s, %s);
            """,
            (movie_id, keyword_id)
        )
    connection.commit()