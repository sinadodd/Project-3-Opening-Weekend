#### Rosina Dodd <br> Project 3 <hr>

# Night at the Movies: Opening Weekend Box Office Predictor

### Table of Contents
- Initial Proposal	<br>
- Scope Changes, Limitations, Other Notes<br>	
- Final Product	<br>
- Progress Log	<br>
<hr>

## Initial Proposal
#### Summary
Estimate a movie’s opening weekend box office results.

#### Data Sources
boxofficemojo.com<br>
TheMovieDB.org - API (rate limiting: 40 requests every 10 seconds)

#### GitHub repository
https://github.com/sinadodd/Project-3-Opening-Weekend

#### Scope Changes, Limitations, Other Notes
- Weekend equals Fri-Sat-Sun. Movies that do not have a 3-day opening gross are not included in data.
- “Opening weekend” is first weekend of wide release.
- Earliest movie is 1980
- Data is from movies with opening weekend results of $10mil and greater.
- Writers incl job title “Screenplay”.
- Producers incl job titles “Executive Producer” and “Associate Producer”.
- Cast is just the top 10 billed.

- DONE - To-do: consider going back and NOT including year.
- DONE - To-do: Not yet saving encoders specifically right now. Come back later to make sure all variable names are unique and correct.
- DONE - To-do: consider coming back later to add "Production Companies" to the dataset. This can be found in the movie details API call.
- To-do: consider coming back later to scrape sites to make dataset bigger. BOM has more movies’ opening weekend data but other data may be incomplete for smaller movies.
<hr>

## Final Product
#### Heroku app
https://opening-weekend-predictor.herokuapp.com/#

#### Performance used:
loss: 0.0025 - mse: 0.0025 - mae: 0.0320	

#### Things to discuss
Pickle files https://pythontips.com/2013/08/02/what-is-pickle-in-python/

Hashing features https://en.wikipedia.org/wiki/Feature_hashing

Limiting workers for Heroku dyno https://www.heroku.com/dynos, https://devcenter.heroku.com/articles/python-gunicorn#basic-configuration
<hr>

## Progress Log
#### July 14 - 1 hr
Looked into potential data sources.

From BOXOFFICEMOJO.COM:
Got list of 2,090 movies' opening weekend box office takes. This is going to be the list of movies I use as my dataset.
Includes title, studio, opening weekend gross, number of theaters opening, date

I think I will be getting the remaining data from TMDB (THEMOVIEDB.ORG) 's API.
rating, director(s), writer(s), approx. budget, runtime, genres
Signed up for API key. 

For director IDs, writer IDs, and genres, I will use the dummy function.
#### July 15 - 2.5 hr
Was reminded about OMDB (existence of) by old class activities.
OMDB includes all the stuff that TMDB has but I will try TMDB first because I think OMDB gives a confusing string when listing names:
Example: 'Director': 'Ron Clements, John Musker, Don Hall(co-director), Chris Williams(co-director)'

TMDB: Using a couple movie titles for testing, successfully did API calls using movie titles to get the movie ID, and then using movie ID to get all the info I want.

Converted xlsx from boxofficemojo to Pandas dataframe, removed unnecessary columns and cleaned up column names. Saved as new csv.
#### July 17 - 3 hr
API calls using part of full data (50 movies instead of 2,090).
rating, director(s), writer(s), approx. budget, runtime, genres

Got movie IDs from movie titles. A few give errors so I am removing those for now and might bring them back in later.
NOTE: consider coming back later to add "Production Companies" to the dataset. This can be found in the movie details API call.
Got budget, genres and runtime from one API call.
Got writing team, direction team, production team from one API call.
Got movie rating (PG, R, etc) from one API call.
#### July 19 - 2.5 hr
Reminder to self: Use one-hot encoding to remove value from categories that are numbers (like 1 for January). Use dummy encoding when I have lots of strings (like names). This isn’t really how to decide which to use, but it’s how I’m going to decide.

Going back to try to get the movies that caused errors when getting movie ID. These were due to format:
Movie Title (YEAR)
So I will remove the year suffix from movie titles, split the release date column into YYYY and MM-DD, and change my API calls to use year.

This caused more trouble than I expected. For example: Alice in Wonderland with release year 2010 actually gets too many results that might be correct.

Just to see how many errors I will get with all 2090 movies, I checked and it’s 80-some. 

I will proceed with removing movies that have errors but consider coming back after I know I can get everything working. The API calls took a long time (rate limiting) so I pulled everything for the ~2k movies that I need and saved my dataframe as csv so I can work on it later and not do these API calls again (at least for a while).
#### July 20 - 3 hr
Snag: Started working with the dataframe to prep for ML. Tried get dummies but the columns that have arrays are not working. After some searching, I found MLB MultiLabelBinarizer with is exactly perfect! https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MultiLabelBinarizer.html

When trying MLB, I realized my columns are strings not lists because I read from csv. Had to convert to lists.

The date isn’t going through get dummies well either. Splitting into separate columns for Y, M, and D. One-hot encoding works great, but now I have to figure out how to get the arrays into dataframes! Probably some Pandas basics that I’m not remembering right now.
#### July 21 - 2 hr
Somehow concat and merge wind up making my resultant dataframe more rows. But every dataframe on its own has 1,907 rows. Hammered at this and just went to sleep frustrated. 
#### July 23 - 2.75 hr
Spent a little time making a prelim sketch of how I think the final site should look.

Back to the problem. Since every dataframe is the same length but after merging or contat-ing, the final df is more rows, I am leaving Movie ID in so I can find duplicates.

Exported all the new dataframes to excel to check the data and see if there is some strange misalignment happening and there isn’t! So the issue is definitely simply in the merge and concat processes.

Took me hours to realize I forgot to reset index after I dropped nulls in the very beginning!

Finally getting to training and I can’t use the arrays (from one-hot encoding the dates) in my classes for the scaling. 
https://github.com/scikit-learn-contrib/sklearn-pandas
Figured out how to use scaler on only certain columns.

Now hitting essentially the same error when trying to fit a model:
ValueError: setting an array element with a sequence.
#### July 24 - 2.75 hr
Working on solving the issue with arrays. Realized that one-hot doesn’t make a Pandas-series (column) of arrays like I thought -- it makes a numpy 2D array. So it’s just as good as get_dummies. 
Cleaned data up enough. Split data and applied scaling. Not scaling Y (for now at least). Can now proceed with testing ML models.
#### July 25 - 4.25 hr
Reminder: MSEs aren’t helpful when not scaling Ys.
Tested some regression models. Simple, out-of-the-box with no parameter adjusting.
 
Unscaled X
Scaled X
 
Train Score
Test Score
Train Score
Test Score
Linear Regression
1.0
0.0026657815
1.00
-0.0008301452
Lasso
0.9999994886
-0.4921323685
0.9999994886
-0.4921319154
Ridge
0.3097268661
-0.0136215329
0.9999871870
0.0480520635
ElasticNet
0.9466158393
0.5630996966
0.9448148935
0.5668487619

ElasticNet looks worth pursuing. Removed Year because I think it’s not helpful, especially when planning to use this tool for predicting upcoming or future movies.

 
Scaled X, removed Year
Scaled X and Y, removed Year
 
Train Score
Test Score
Train Score
Test Score
Linear Regression
1.0
-0.32741794420704196
1.0
-0.32788325379749295
Lasso
0.9999986184014481
-0.8443851540331919
0.03869454088908797
0.04490900684128174
Ridge
0.9999659567955441
-0.2031366784834734
0.9999659567955442
-0.20313667848346606
ElasticNet
0.9438555520988579
0.5706165435610289
0.2336431355840808
0.2984492248517925


Moving on to trying neural net.

First pass at using neural net:
nn_model.add(Dense(units=1500, input_dim=16314, activation='relu'))
nn_model.add(Dense(units=800, activation='relu'))
nn_model.add(Dense(units=300, activation='relu'))
nn_model.add(Dense(units=1, activation='linear'))

Fitting with epochs=300.

Evaluating test data:
loss: 0.0025 - mse: 0.0025 - mae: 0.0320
[0.0024977298175224904, 0.0024977298, 0.031986564]
#### July 26 - 6.5 hr
Trying with epochs=100:
loss: 0.0020 - mse: 0.0020 - mae: 0.0298
[0.001969248973090881, 0.0019692492, 0.029752612]

Looked into bootstrap templates. I think it will save time if I just start from scratch and know all the parts I’m using, rather than having to learn the parts of a downloaded template.

Getting index.html pulled together. A lot of bootstrap cards. https://www.bootstrapdash.com/bootstrap-4-tutorial/card/
Starting flask app.
Going back through all ML parts to save helpers to make prediction on the user’s movie selection.
#### July 27 - 5 hr
#### July 28 - 8 hr
Instead of csv, using gzipped pickle files because they’re faster and preserve the datatypes. Bonus: Pandas has to_ and read_ pickle.
#### July 29 - 4 hr
#### July 30 - 5 hr
#### July 31 - 5 hr
Add top ten cast. Removed Distributor and adding in Production Studios. Easier to only have Y from boxofficemojo and have all the X (features) from the tmdb API calls.

Lion King with 50 epochs $60,145,564.
935 seconds to train 300 epochs.
Lion King with 300 epochs is $192,121,824.

Heroku app failed when ML model got more complex. Edited gunicorn settings so there is only 1 worker. App works but only one user at a time.
#### August 1 - Presentation Prep
Added card for cast.
Worked on readme.
