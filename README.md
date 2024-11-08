# soen363-assignment2

stinky asf

### Creating a python virtual environment (I did it on WSL):
<ol>
<li>In git bash, navigate to the directory of the project </li>
<li>In the bash terminal, type the following to create the virtual environment: python -m venv venv </li>
<li>To activate it, type: source ./venv/Scripts/activate (it works if you see (venv))</li>
</ol>

### Packages to install
To be able to work with postgres, install the following: <i>pip install psycopg2</i> <br>
Request library to send GET requests to APIs: <i>pip install requests</i>
Install package to be able to read .env files: <i>pip install python-dotenv</i>

### .env File
In the root directory, create a .env file --> click on create a new file and name it .env <br>
Include the following: <br>
DB_HOST=localhost <br>
DB_NAME={name of the new db you create i called it 363-A2} <br>
DB_USER={your username on postgres, is most probably postgres} <br>
DB_PASSWORD={your password on postgres} <br>
DATABASE_URL=postgres://{replace with your username}:{replace with your password}@localhost:5432/363-A2
