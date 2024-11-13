# soen363-assignment2

These files are used to populate the tables in the Postgres database with a single instance. The movie picked is Twilight with the imdb_id tt1099212. The file titled populate_baseTables.py populates the tables that do not have any foreign keys, so the genre content rating, keyword, language, country, actor, director tables. The file populate_movie.py populates the movie table. Finally, the file populate_relationships.py populates all the tables that have foreign keys so movie_aka and all the relationships between movie and the base tables. The running order is to start with either populate_baseTables or populate_movie, then to run the second file (the one you did not start with) and finally to run populate_relationships.

### Creating a python virtual environment (I did it on WSL):
<ol>
<li>In git bash, navigate to the directory of the project </li>
<li>In the bash terminal, type the following to create the virtual environment: python -m venv venv </li>
<li>To activate it, type: source ./venv/Scripts/activate (it works if you see (venv))</li>
</ol>

### Packages to install
To be able to work with postgres, install the following: <i>pip install psycopg2</i> <br>
Request library to send GET requests to APIs: <i>pip install requests</i> <br>
Install package to be able to read .env files: <i>pip install python-dotenv</i>

### .env File
In the root directory, create a .env file --> click on create a new file and name it .env <br>
Include the following: <br>
DB_HOST=localhost <br>
DB_NAME={name of the new db you create i called it 363-A2} <br>
DB_USER={your username on postgres, is most probably postgres} <br>
DB_PASSWORD={your password on postgres} <br>
DATABASE_URL=postgres://{replace with your username}:{replace with your password}@localhost:5432/{replace with your db_name}
RAPIDAPI_KEY={replace with your rapid api key}
RAPIDAPI_HOST=watchmode.p.rapidapi.com
