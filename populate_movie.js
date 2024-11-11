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

// Your RapidAPI key for the Watchmode API
const RAPIDAPI_KEY = 'd044bde95amshea8beb39be77448p19cb8ejsn44384da3c58b'; // Replace with your actual API key

// Connect to the database
client.connect()
  .then(() => console.log('Connected to PostgreSQL'))
  .catch(err => console.error('Error connecting to PostgreSQL', err.stack));

// API URL to fetch movie details
const imdbApiUrl = 'https://search.imdbot.workers.dev/?tt=tt0107688';

axios.get(imdbApiUrl)
  .then(async (response) => {
    const jsonResponse = response.data;
    const shortData = jsonResponse.short;

    // Fetching movie details
    const movieTitle = shortData.name || '';
    const plot = shortData.description || '';
    const rating = shortData.aggregateRating?.ratingValue || null;
    const viewersRating = rating ? parseFloat(rating) : null;
    const releaseYear = shortData.datePublished ? parseInt(shortData.datePublished.slice(0, 4)) : null;
    const imdbId = jsonResponse.imdbId || null;

    // Fetch tmdb_id and watchmode_id using the Watchmode API
    let tmdbId = null;
    let watchmodeId = null;

    if (imdbId) {
      // Use the URL format you specified
      const watchmodeApiUrl = `https://watchmode.p.rapidapi.com/search/?search_field=imdb_id&search_value=${imdbId}&types=movie`;
      const headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': 'watchmode.p.rapidapi.com',
      };

      try {
        const watchmodeResponse = await axios.get(watchmodeApiUrl, { headers });
        const titleResults = watchmodeResponse.data.title_results;

        if (titleResults && titleResults.length > 0) {
          // Extracting tmdb_id and watchmode_id from the first result
          tmdbId = titleResults[0]?.tmdb_id || null;
          watchmodeId = titleResults[0]?.id || null;
        }
      } catch (err) {
        console.error('Error fetching data from Watchmode API:', err.message);
      }
    }

    // Insert movie data into the movie table (simplified without content rating, country, or language)
    try {
      const checkMovieQuery = `SELECT id FROM movie WHERE tmdb_id = $1 LIMIT 1`;
      const checkResult = await client.query(checkMovieQuery, [tmdbId]);

      if (checkResult.rows.length === 0) {
        const insertMovieQuery = `
          INSERT INTO movie 
            (title, plot, viewers_rating, release_year, 
             watchmode_id, tmdb_id, imdb_id) 
           VALUES 
            ($1, $2, $3, $4, $5, $6, $7)
           ON CONFLICT (tmdb_id) DO NOTHING;
        `;

        const values = [
          movieTitle,
          plot,
          viewersRating,
          releaseYear,
          watchmodeId,
          tmdbId,
          imdbId,
        ];

        const result = await client.query(insertMovieQuery, values);

        if (result.rowCount > 0) {
          console.log(`Inserted movie: ${movieTitle}`);
        }
      } else {
        console.log(`Movie already exists: ${movieTitle}`);
      }

    } catch (err) {
      console.error('Error inserting movie:', err.stack);
    }
  })
  .catch((error) => {
    console.error('Error fetching data from IMDb API:', error.message);
  })
  .finally(() => {
    client.end();
  });
