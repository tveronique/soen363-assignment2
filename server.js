const axios = require('axios');
const { Client } = require('pg');

// Set up your database connection
const client = new Client({
  host: 'localhost',
  port: 5432,
  user: 'postgres',
  password: 'jiro', // replace with your password
  database: 'A2_363', // replace with your DB name
});

// Connect to the database
client.connect()
  .then(() => console.log('Connected to PostgreSQL'))
  .catch(err => console.error('Error connecting to PostgreSQL', err.stack));

// API URL to fetch movie details (adjust based on your API)
const apiUrl = 'https://search.imdbot.workers.dev/?tt=tt0107688';

axios.get(apiUrl)
  .then(async (response) => {
    const data = response.data.short;

    // 1. Populate Genres
    const genres = data.genre || [];
    for (let genre of genres) {
      try {
        const result = await client.query(
          'SELECT id FROM genre WHERE name = $1',
          [genre]
        );
        if (result.rows.length === 0) {
          await client.query(
            'INSERT INTO genre (name) VALUES ($1)',
            [genre]
          );
        }
      } catch (err) {
        console.error('Error inserting genre:', err.stack);
      }
    }

    // 2. Populate Content Rating
    const contentRating = data.contentRating || null;
    if (contentRating) {
      try {
        const result = await client.query(
          'SELECT id FROM content_rating WHERE rating = $1',
          [contentRating]
        );
        if (result.rows.length === 0) {
          await client.query(
            'INSERT INTO content_rating (rating) VALUES ($1)',
            [contentRating]
          );
        }
      } catch (err) {
        console.error('Error inserting content rating:', err.stack);
      }
    }

    // 3. Populate Actors
    const actors = data.actor || [];
    for (let actor of actors) {
      if (actor && actor.name) {
        try {
          const result = await client.query(
            'SELECT id FROM actor WHERE name = $1',
            [actor.name]
          );
          if (result.rows.length === 0) {
            await client.query(
              'INSERT INTO actor (name) VALUES ($1)',
              [actor.name]
            );
          }
        } catch (err) {
          console.error('Error inserting actor:', err.stack);
        }
      }
    }

    // 4. Populate Directors
    const directors = data.director || [];
    for (let director of directors) {
      if (director && director.name) {
        try {
          const result = await client.query(
            'SELECT id FROM director WHERE name = $1',
            [director.name]
          );
          if (result.rows.length === 0) {
            await client.query(
              'INSERT INTO director (name) VALUES ($1)',
              [director.name]
            );
          }
        } catch (err) {
          console.error('Error inserting director:', err.stack);
        }
      }
    }

    // 5. Populate Keywords
    const keywords = data.keywords ? data.keywords.split(',') : [];
    for (let keyword of keywords) {
      try {
        const result = await client.query(
          'SELECT id FROM keyword WHERE word = $1',
          [keyword.trim()]
        );
        if (result.rows.length === 0) {
          await client.query(
            'INSERT INTO keyword (word) VALUES ($1)',
            [keyword.trim()]
          );
        }
      } catch (err) {
        console.error('Error inserting keyword:', err.stack);
      }
    }

    // 6. Populate Languages
    const languages = response.data.main.spokenLanguages?.spokenLanguages || [];
    for (let language of languages) {
      if (language && language.text) {
        try {
          const result = await client.query(
            'SELECT id FROM language WHERE name = $1',
            [language.text]
          );
          if (result.rows.length === 0) {
            await client.query(
              'INSERT INTO language (name) VALUES ($1)',
              [language.text]
            );
          }
        } catch (err) {
          console.error('Error inserting language:', err.stack);
        }
      }
    }

    // 7. Populate Countries
    const countries = response.data.main.countriesOfOrigin.countries || [];
    for (let country of countries) {
      const countryName = country.text; // e.g., "United States", "United Kingdom"
      const countryCode = country.id;   // e.g., "US", "GB"

      try {
        const result = await client.query(
          'SELECT country_id FROM country WHERE country_code = $1',
          [countryCode]
        );
        if (result.rows.length === 0) {
          await client.query(
            'INSERT INTO country (country_name, country_code) VALUES ($1, $2)',
            [countryName, countryCode]
          );
        }
      } catch (err) {
        console.error('Error inserting country:', err.stack);
      }
    }


  })
  .catch((error) => {
    console.error('Error fetching data from API:', error.message);
  })
  .finally(() => {
    client.end();
  });
