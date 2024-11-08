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


def fetch_all_genres():
    genres = set() 
    url = "https://search.imdbot.workers.dev/?tt=tt1099212"  # for Twilight

    # Make the GET request to the API
    response = requests.get(url)
    
    # Print the status code and the raw JSON response to debug
    print("Response Status Code:", response.status_code)
    try:
        json_response = response.json()  # Parse JSON response
        print("Response JSON:", json_response)  # Print the JSON response to see the structure
    except ValueError:
        print("Error: The response is not valid JSON.")
        return genres

    # Check if the request was successful
    if response.status_code == 200:
        # Extract genres from the 'short' part of the response
        short_data = json_response.get("short", {})
        movie_genres = short_data.get("genre", [])
        
        if isinstance(movie_genres, list):
            genres.update(movie_genres)  # Add genres to the set
    else:
        print(f"Error fetching data: {response.status_code}")

    return genres

# Function to insert genres into the genre table if they don't already exist
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

# Main function to populate the genre table
def populate_genres_from_api():
    genres = fetch_all_genres()
    print("genres:", genres)
    for genre in genres:
        insert_genre(genre)
    print("Genres populated successfully.")

# Run the populate_genres_from_api function to insert to the genre table
populate_genres_from_api()