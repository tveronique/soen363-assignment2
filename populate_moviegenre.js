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
const imdbApiUrl = 'https://search.imdbot.workers.dev/?tt=tt0117571';

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
    const genres = data.genre || []; 
    const actors = data.actor || []; 
    const directors = data.director || [];
    const keywords = data.keywords ? data.keywords.split(',') : [];
    const languages = response.data.main.spokenLanguages?.spokenLanguages || [];
    const contentRating = data.contentRating || null;
    const countries = response.data.main.countriesOfOrigin.countries || [];
    const akaData = response.data.main.akas?.edges || [];
  

    // Process genres
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

    // Process actors
for (const actor of actors) {
    const actorName = actor.name; // Access the 'name' property from the actor object
    if (actorName) {
      try {
        // Find the actor ID in the actor table
        const actorQuery = 'SELECT id FROM actor WHERE name = $1 LIMIT 1';
        const actorResult = await client.query(actorQuery, [actorName]);
  
        if (actorResult.rows.length === 0) {
          console.log(`Actor '${actorName}' not found in the database.`);
          continue; // Skip if actor is not found
        }
  
        const actorId = actorResult.rows[0].id;
  
        // Check if the (movie_id, actor_id) already exists in movie_actor
        const checkActorQuery = `
          SELECT 1 FROM movie_actor 
          WHERE movie_id = $1 AND actor_id = $2
          LIMIT 1;
        `;
        const checkActorResult = await client.query(checkActorQuery, [movieId, actorId]);
  
        if (checkActorResult.rows.length === 0) {
          // Insert the (movie_id, actor_id) pair into movie_actor
          const insertActorQuery = `
            INSERT INTO movie_actor (movie_id, actor_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING;
          `;
          await client.query(insertActorQuery, [movieId, actorId]);
          console.log(`Inserted actor '${actorName}' for movie ID ${movieId}`);
        } else {
          console.log(`Actor '${actorName}' already linked to movie ID ${movieId}`);
        }
      } catch (err) {
        console.error(`Error processing actor '${actorName}':`, err.stack);
      }
    } else {
      console.log('Actor name is missing in the API data.');
    }
  }

  for (const director of directors) {
    const directorName = director.name; 
    if (directorName) {
      try {
        // Find the director ID in the director table
        const directorQuery = 'SELECT id FROM director WHERE name = $1 LIMIT 1';
        const directorResult = await client.query(directorQuery, [directorName]);

        if (directorResult.rows.length === 0) {
          console.log(`Director '${directorName}' not found in the database.`);
          continue; // Skip if director is not found
        }

        const directorId = directorResult.rows[0].id;

        // Check if the (movie_id, director_id) already exists in movie_director
        const checkDirectorQuery = `
          SELECT 1 FROM movie_director 
          WHERE movie_id = $1 AND director_id = $2
          LIMIT 1;
        `;
        const checkDirectorResult = await client.query(checkDirectorQuery, [movieId, directorId]);

        if (checkDirectorResult.rows.length === 0) {
          // Insert the (movie_id, director_id) pair into movie_director
          const insertDirectorQuery = `
            INSERT INTO movie_director (movie_id, director_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING;
          `;
          await client.query(insertDirectorQuery, [movieId, directorId]);
          console.log(`Inserted director '${directorName}' for movie ID ${movieId}`);
        } else {
          console.log(`Director '${directorName}' already linked to movie ID ${movieId}`);
        }
      } catch (err) {
        console.error(`Error processing director '${directorName}':`, err.stack);
      }
    } else {
      console.log('Director name is missing in the API data.');
    }
  }

  for (let keyword of keywords) {
    try {
      const trimmedKeyword = keyword.trim(); // Trim any extra spaces

      // Find the keyword ID in the keyword table
      const keywordQuery = 'SELECT id FROM keyword WHERE word = $1 LIMIT 1';
      const keywordResult = await client.query(keywordQuery, [trimmedKeyword]);

      if (keywordResult.rows.length === 0) {
        console.log(`Keyword '${trimmedKeyword}' not found in the database.`);
        continue;
      }

      // Now get the keyword ID
      const keywordId = keywordResult.rows[0].id;

      // Check if the (movie_id, keyword_id) already exists in movie_keyword
      const checkKeywordQuery = `
        SELECT 1 FROM movie_keyword 
        WHERE movie_id = $1 AND keyword_id = $2
        LIMIT 1;
      `;
      const checkKeywordResult = await client.query(checkKeywordQuery, [movieId, keywordId]);

      if (checkKeywordResult.rows.length === 0) {
        // Insert the (movie_id, keyword_id) pair into movie_keyword
        const insertKeywordQuery = `
          INSERT INTO movie_keyword (movie_id, keyword_id)
          VALUES ($1, $2)
          ON CONFLICT DO NOTHING;
        `;
        await client.query(insertKeywordQuery, [movieId, keywordId]);
        console.log(`Inserted keyword '${trimmedKeyword}' for movie ID ${movieId}`);
      } else {
        console.log(`Keyword '${trimmedKeyword}' already linked to movie ID ${movieId}`);
      }
    } catch (err) {
      console.error(`Error processing keyword '${keyword}':`, err.stack);
    }
  }

  for (const language of languages) {
    try {
      // Find the language ID in the language table
      const languageQuery = 'SELECT id FROM language WHERE name = $1 LIMIT 1';
      const languageResult = await client.query(languageQuery, [language.text]);

      if (languageResult.rows.length === 0) {
        console.log(`Language '${language.text}' not found in the database. Skipping.`);
        continue; // Skip if the language is not found
      }

      // Now get the language ID
      const languageId = languageResult.rows[0].id;

      // Check if the (movie_id, language_id) already exists in movie_language
      const checkLanguageQuery = `
        SELECT 1 FROM movie_language 
        WHERE movie_id = $1 AND language_id = $2
        LIMIT 1;
      `;
      const checkLanguageResult = await client.query(checkLanguageQuery, [movieId, languageId]);

      if (checkLanguageResult.rows.length === 0) {
        // Insert the (movie_id, language_id) pair into movie_language
        const insertLanguageQuery = `
          INSERT INTO movie_language (movie_id, language_id)
          VALUES ($1, $2)
          ON CONFLICT DO NOTHING;
        `;
        await client.query(insertLanguageQuery, [movieId, languageId]);
        console.log(`Inserted language '${language.text}' for movie ID ${movieId}`);
      } else {
        console.log(`Language '${language.text}' already linked to movie ID ${movieId}`);
      }
    } catch (err) {
      console.error(`Error processing language '${language.text}':`, err.stack);
    }
  }

  if (contentRating) {
    try {
      // Query to check if the content rating exists in the 'content_rating' table
      const contentRatingResult = await client.query(
        'SELECT id FROM content_rating WHERE rating = $1',
        [contentRating]
      );
  
      if (contentRatingResult.rows.length > 0) {
        // Get the content rating ID
        const contentRatingId = contentRatingResult.rows[0].id;
  
        // Check if the (movie_id, content_rating_id) pair already exists in the movie_contentrating table
        const checkContentRatingQuery = `
          SELECT 1 FROM movie_contentrating 
          WHERE movie_id = $1 AND content_rating_id = $2
          LIMIT 1;
        `;
        const checkContentRatingResult = await client.query(checkContentRatingQuery, [movieId, contentRatingId]);
  
        if (checkContentRatingResult.rows.length === 0) {
          // If not already linked, insert the pair into the movie_contentrating table
          await client.query(
            'INSERT INTO movie_contentrating (movie_id, content_rating_id) VALUES ($1, $2) ON CONFLICT DO NOTHING',
            [movieId, contentRatingId]
          );
          console.log(`Inserted content rating '${contentRating}' for movie ID ${movieId}`);
        } else {
          console.log(`Content rating '${contentRating}' already linked to movie ID ${movieId}`);
        }
      } else {
        console.log(`Content rating '${contentRating}' not found in the database.`);
      }
    } catch (err) {
      console.error('Error inserting movie-contentrating relationship:', err.stack);
    }
  }

  for (const country of countries) {
    try {
      // Find the country ID in the country table
      const countryQuery = 'SELECT country_id FROM country WHERE country_name = $1 LIMIT 1';
      const countryResult = await client.query(countryQuery, [country.text]);
  
      if (countryResult.rows.length === 0) {
        console.log(`Country '${country.text}' not found in the database. Skipping.`);
        continue; // Skip if the country is not found
      }
  
      // Now get the country ID
      const countryId = countryResult.rows[0].country_id;
  
      // Check if the (movie_id, country_id) already exists in movie_country
      const checkCountryQuery = `
        SELECT 1 FROM movie_country 
        WHERE movie_id = $1 AND country_id = $2
        LIMIT 1;
      `;
      const checkCountryResult = await client.query(checkCountryQuery, [movieId, countryId]);
  
      if (checkCountryResult.rows.length === 0) {
        // Insert the (movie_id, country_id) pair into movie_country
        const insertCountryQuery = `
          INSERT INTO movie_country (movie_id, country_id)
          VALUES ($1, $2)
          ON CONFLICT DO NOTHING;
        `;
        await client.query(insertCountryQuery, [movieId, countryId]);
        console.log(`Inserted country '${country.text}' for movie ID ${movieId}`);
      } else {
        console.log(`Country '${country.text}' already linked to movie ID ${movieId}`);
      }
    } catch (err) {
      console.error(`Error processing country '${country.text}':`, err.stack);
    }
  }

  for (const akaEdge of akaData) {
    const akaTitle = akaEdge.node?.text?.trim();  // Get the aka_title from the node
  
    if (akaTitle) {
      try {
        // Check if the movie already exists in the movie table (you already have movieId)
        const movieQuery = 'SELECT id FROM movie WHERE imdb_id = $1 LIMIT 1';
        const movieResult = await client.query(movieQuery, [imdbId]);  // Assuming imdbId is available
  
        if (movieResult.rows.length === 0) {
          console.log(`Movie with IMDb ID ${imdbId} not found in the database.`);
          continue; // Skip if the movie is not found in the database
        }
  
        const movieId = movieResult.rows[0].id;
  
        // Check if the (aka_title, movie_id) pair already exists in movie_aka
        const checkAkaQuery = `
          SELECT 1 FROM movie_aka 
          WHERE aka_title = $1 AND movie_id = $2
          LIMIT 1;
        `;
        const checkAkaResult = await client.query(checkAkaQuery, [akaTitle, movieId]);
  
        if (checkAkaResult.rows.length === 0) {
          // Insert the (aka_title, movie_id) pair into movie_aka
          const insertAkaQuery = `
            INSERT INTO movie_aka (aka_title, movie_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING;
          `;
          await client.query(insertAkaQuery, [akaTitle, movieId]);
          console.log(`Inserted alternate title '${akaTitle}' for movie ID ${movieId}`);
        } else {
          console.log(`Alternate title '${akaTitle}' already linked to movie ID ${movieId}`);
        }
      } catch (err) {
        console.error(`Error processing alternate title '${akaTitle}':`, err.stack);
      }
    } else {
      console.log('Aka title is missing or invalid.');
    }
  }
  

  
  })
  .catch((error) => {
    console.error('Error fetching data from IMDb API:', error.message);
  })
  .finally(() => {
    client.end();
  });
