# Project-3-Opening-Weekend

### July 14 - 1 hr

Looked into potential data sources.

From BOXOFFICEMOJO.COM:
Got list of 2,090 movies' opening weekend box office takes. This is going to be the list of movies I use as my dataset.
  Note:
    * Weekend equals Fri-Sat-Sun. Movies that do not have a 3-day opening gross are not included on this chart.
    ^ Total Gross does not include additional releases, if any.
    ** First weekend of wide release.
Includes title, studio, opening weekend gross, number of theaters opening, date

I think I will be getting the remaining data from TMDB (THEMOVIEDB.ORG) 's API.
rating, director(s), writer(s), approx. budget, runtime, genres
Signed up for API key.

For director IDs, writer IDs, and genres, I will use the dummy function.

### July 15 - 2.5 hr

Was reminded about OMDB (existence of) by old class activities.
  OMDB includes all the stuff that TMDB has but I will try TMDB first because I think OMDB gives a confusing string when listing names:
    example:
    'Director': 'Ron Clements, John Musker, Don Hall(co-director), Chris Williams(co-director)'

TMDB: Using a couple movie titles for testing, successfully did API calls using movie titles to get the movie ID, and then using movie ID to get all the info I want.

Converted xlsx from boxofficemojo to Pandas dataframe, removed unnecessary columns and cleaned up column names. Saved as new csv.

### July 17 - 3 hours

API calls using part of full data (50 movies instead of 2,090).
rating, director(s), writer(s), approx. budget, runtime, genres

Got movie IDs from movie titles. A few give errors so I am removing those for now and might bring them back in later.
NOTE: consider coming back later to add "Production Companies" to the dataset. This can be found in the movie details API call.
Got budget, genres and runtime from one API call.
Got writing team, direction team, production team from one API call.
Got movie rating (PG, R, etc) from one API call.

Plan to go back to try to get the movies that caused errors when getting movie ID. These were due to format:
Movie Title (YEAR)
So I will remove the year suffix from movie titles, split the release date column into YYYY and MM-DD, and change my API calls to use year.



























NOTE: consider coming back later to add "Production Companies" to the dataset. This can be found in the movie details API call.