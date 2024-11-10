const axios = require('axios');
const { Client } = require('pg');

// Set up your database connection
const client = new Client({
  host: 'localhost',
  port: 5432,
  user: 'postgres',
  password: 'jiro', // Replace with your password
  database: 'A2_363', // Replace with your DB name
});

// Connect to the database
client.connect()
  .then(() => console.log('Connected to PostgreSQL'))
  .catch(err => console.error('Error connecting to PostgreSQL', err.stack));

// IMDb API URL to fetch movie details
const imdbApiUrl = 'https://search.imdbot.workers.dev/?tt=tt1099212';

axios.get(imdbApiUrl)
  .then(async (response) => {
    const data = response.data.short;
    const imdbId = response.data.imdbId || null;

    // Fetch the movie details from the database
    const movieQuery = 'SELECT id FROM movie WHERE imdb_id = $1 LIMIT 1';
    const movieResult = await client.query(movieQuery, [imdbId]);
    
    if (movieResult.rows.length === 0) {
      console.log(`Movie with IMDb ID ${imdbId} not found in the database.`);
      return;
    }

    const movieId = movieResult.rows[0].id;

    // Fetch genres from the API response
    const genres = data.genre || []; // List of genre names, e.g., ["Action", "Comedy"]

    for (const genreName of genres) {
      try {
        // Find the genre ID in the genre table
        const genreQuery = 'SELECT id FROM genre WHERE name = $1 LIMIT 1';
        const genreResult = await client.query(genreQuery, [genreName]);

        if (genreResult.rows.length === 0) {
          console.log(`Genre '${genreName}' not found in the database.`);
          continue; // Skip if genre is not found
        }

        const genreId = genreResult.rows[0].id;

        // Check if the (movie_id, genre_id) already exists in movie_genre
        const checkQuery = `
          SELECT 1 FROM movie_genre 
          WHERE movie_id = $1 AND genre_id = $2
          LIMIT 1;
        `;
        const checkResult = await client.query(checkQuery, [movieId, genreId]);

        if (checkResult.rows.length === 0) {
          // Insert the (movie_id, genre_id) pair into movie_genre
          const insertQuery = `
            INSERT INTO movie_genre (movie_id, genre_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING;
          `;
          await client.query(insertQuery, [movieId, genreId]);
          console.log(`Inserted genre '${genreName}' for movie ID ${movieId}`);
        } else {
          console.log(`Genre '${genreName}' already linked to movie ID ${movieId}`);
        }
      } catch (err) {
        console.error(`Error processing genre '${genreName}':`, err.stack);
      }
    }
  })
  .catch((error) => {
    console.error('Error fetching data from IMDb API:', error.message);
  })
  .finally(() => {
    client.end();
  });
