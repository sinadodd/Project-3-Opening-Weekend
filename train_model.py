import json
import time
import timeit
import traceback

import numpy as np
import pandas as pd
from keras import Sequential
from keras.layers import Dense
from requests import HTTPError, Response
from sklearn.feature_extraction import FeatureHasher
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, MinMaxScaler

from helpers import ScalingHelpers, TrainingHelpers
from tmdb_api import get_tmdb_id_from_title, load_from_tmdb, parse_json

# Important filenames
BOX_OFFICE_MOJO_XLS = "Resources/openingweekend_boxofficemojo.xlsx"
OPENINGWEEKEND_PICKLE = "Resources/openingweekend.pickle.gz"
OPENINGWEEKEND_WITH_TMDB_IDS_PICKLE = "Resources/openingweekend_ids.pickle.gz"
MERGED_JSON_PICKLE = "Resources/tmdb_json.pickle.gz"
MERGE_ERRORS_ID_PICKLE = "Resources/merge_errors_id.pickle.gz"
MERGE_ERRORS_JSON_PICKLE = "Resources/merge_errors_json.pickle.gz"
PARSED_JSON_PICKLE = "Resources/parsed_json.pickle.gz"
FEATURES_PICKLE = "Resources/features.pickle.gz"
SEQUENTIAL_NN_MODEL_H5 = "Resources/sequential_nn_model.h5"
TRAINING_HELPERS_PICKLE = "Resources/training_helpers.pickle.gz"
NN_HELPERS_PICKLE = "Resources/nn_helpers.pickle.gz"
NN_TRAIN_DATA_PICKLE = "Resources/nn_train_data.pickle.gz"
NN_TEST_DATA_PICKLE = "Resources/nn_test_data.pickle.gz"


def save_box_office_mojo_csv() -> None:
    """ Load the Box Office Mojo excel spreadsheet and rename/drop columns.
    Save the result as a gzipped pickle file. """
    start = time.time()
    print(f"Loading excel file {BOX_OFFICE_MOJO_XLS}...")
    df = pd.read_excel(BOX_OFFICE_MOJO_XLS)
    print("Done.")
    df = df.rename(columns={"Title (click to view)": "Title",
                            "Opening*": "Opening",
                            "Date**": "Date"})
    df = df.drop(['% of Total', 'Total Gross^', 'Rank', 'Avg.'], axis=1)

    print(f"BoxOfficeMojo spreadsheet: {df.shape}")
    print("Writing output files...")
    df.to_pickle(OPENINGWEEKEND_PICKLE)
    print(f"{OPENINGWEEKEND_PICKLE} done")
    print(f"save_box_office_mojo_csv: {time.time() - start:.1f}s")


def get_tmdb_ids() -> None:
    """ Load the Box Office Mojo data and determine the TMDB ID for each entry.
    Save the result as a gzipped pickle file. """
    print(f"Loading pickle file {OPENINGWEEKEND_PICKLE}...")
    bom_df = pd.read_pickle(OPENINGWEEKEND_PICKLE)
    print("Done.")

    out_cols = list(bom_df.columns) + [
        "ID",
        "Drop Reason",
    ]

    seen_titles = set()
    seen_ids = set()
    total_rows = len(bom_df.index)
    processed_rows = 0
    start = time.time()
    report = start + 5
    error_count = 0

    out_data = []
    for row_tuple in bom_df.itertuples(index=False):
        title = row_tuple.Title
        release_date = row_tuple.Date
        errors = []
        tmdb_id = None
        processed_rows += 1
        t = time.time()
        if t > report:
            elapsed = t - start
            rate = processed_rows / elapsed
            print(f"Processed {processed_rows}/{total_rows} in {elapsed:.1f}s ({rate:.2f}/s) - "
                  f"{error_count} errors")
            report += 5

        if title in seen_titles:
            errors.append(f"Duplicate title: {title}")
        else:
            seen_titles.add(title)

        if not errors:
            for retry in range(5):
                try:
                    tmdb_id = get_tmdb_id_from_title(title, release_date.year)
                except HTTPError as e:
                    if e.response.status_code == 429:
                        response: Response = e.response
                        wait = int(response.headers.get("Retry-After")) + 1
                        print(f"Got HTTP 429; retrying in {wait} seconds...")
                        time.sleep(wait)
                        # Retry
                        continue
                    else:
                        errors.append(str(e))
                        # Don't retry
                except Exception as e:
                    traceback.print_exc()
                    errors.append(str(e))
                    # Don't retry
                break
            else:
                # Retries exceeded
                errors.append("Too many retries")

        if tmdb_id:
            if tmdb_id in seen_ids:
                errors.append(f"Duplicate ID {tmdb_id} for title {title}")
            else:
                seen_ids.add(tmdb_id)

        if not tmdb_id and not errors:
            errors = ["No TMDB ID found"]

        if errors:
            print(f"{title}: {errors}")
            error_count += 1

        out_data.append(list(row_tuple) + [
            tmdb_id,
            "; ".join(errors) or None
        ])

    with_tmdb_ids_df = pd.DataFrame(out_data, columns=out_cols)

    print(f"Data with IDs: {with_tmdb_ids_df.shape} / errors: {with_tmdb_ids_df['Drop Reason'].count()}")
    print("Writing output files...")
    with_tmdb_ids_df[with_tmdb_ids_df["Drop Reason"].isnull()]\
        .drop(columns="Drop Reason").to_pickle(OPENINGWEEKEND_WITH_TMDB_IDS_PICKLE)
    with_tmdb_ids_df[with_tmdb_ids_df["Drop Reason"].notnull()].to_pickle(MERGE_ERRORS_ID_PICKLE)
    print(f"get_tmdb_ids: {time.time() - start:.1f}s")


def get_tmdb_json() -> None:
    """ Load the JSON details for each movie we have a TMDB ID for.
    Save the result as a gzipped pickle file. """
    start = time.time()
    print(f"Loading pickle file {OPENINGWEEKEND_WITH_TMDB_IDS_PICKLE}...")
    with_tmdb_ids_df = pd.read_pickle(OPENINGWEEKEND_WITH_TMDB_IDS_PICKLE)
    print("Done.")

    out_cols = list(with_tmdb_ids_df.columns) + [
            "Drop Reason", "JSON"
        ]

    total_rows = len(with_tmdb_ids_df.index)

    processed_rows = 0
    start = time.time()
    report = start + 5
    error_count = 0

    out_data = []
    for row_tuple in with_tmdb_ids_df.itertuples(index=False):
        processed_rows += 1
        t = time.time()
        if t > report:
            elapsed = t - start
            rate = processed_rows / elapsed
            print(f"Processed {processed_rows}/{total_rows} in {elapsed:.1f}s ({rate:.2f}/s) - "
                  f"{error_count} errors")
            report += 5

        (tmdb_data, error, json_resp) = load_from_tmdb(row_tuple.ID)

        out_data.append(list(row_tuple) + [
            error, json_resp
        ])
        if error:
            error_count += 1

    df = pd.DataFrame(out_data, columns=out_cols)

    print(f"Combined data {df.shape} / errors: {df['Drop Reason'].count()}")
    print("Writing output files...")
    df[df["Drop Reason"].isnull()].drop(columns="Drop Reason").to_pickle(MERGED_JSON_PICKLE)
    df[df["Drop Reason"].notnull()].to_pickle(MERGE_ERRORS_JSON_PICKLE)
    print(f"{MERGE_ERRORS_JSON_PICKLE} done")
    print(f"get_tmdb_json: {time.time() - start:.1f}s")


def parse_json_responses() -> None:
    """ Parse the JSON details for each movie into columns we'll use for features.
    Save the result as a gzipped pickle file. """
    start = time.time()
    print(f"Loading pickle file {MERGED_JSON_PICKLE}...")
    json_df = pd.read_pickle(MERGED_JSON_PICKLE)
    print("Done.")

    out_cols = list(json_df.columns) + [
        "Drop Reason",
        "Budget", "Runtime",
        "Genres", "Directing", "Producing", "Writing",
        "Cast",
        "Rating", "Keywords", "Studios",
        "Raw Data",
    ]

    out_data = []
    for row_tuple in json_df.itertuples(index=False):
        sample, err = parse_json(row_tuple.ID, json.loads(row_tuple.JSON))
        out_data.append(list(row_tuple) + [
            err,
            sample.budget, sample.runtime,
            sample.genres, sample.directors, sample.producers, sample.writers,
            sample.cast,
            sample.rating, sample.keywords, sample.studios,
            sample
        ])

    df = pd.DataFrame(out_data, columns=out_cols)
    print(f"Parsed JSON data {df.shape} / errors: {df['Drop Reason'].count()}")
    print("Writing output files...")
    df[df["Drop Reason"].isnull()].drop(columns="Drop Reason").to_pickle(PARSED_JSON_PICKLE)
    print(f"parse_json_responses: {time.time() - start:.1f}s")


def create_features_from_merged_df() -> None:
    """ Transform the combined input data into features useful for ML algorithms.
    Save the result as a gzipped pickle file. """
    start = time.time()
    helpers = TrainingHelpers()

    print(f"Loading {PARSED_JSON_PICKLE}...")
    df = pd.read_pickle(PARSED_JSON_PICKLE)
    print("Done.")

    print(f"Starting feature creation: {df.shape} - {list(df.columns)}")

    df = df.dropna(axis='columns', how='all').dropna()
    df.reset_index(inplace=True, drop=True)

    print(f"Dropping na columns/rows; {df.shape} - {list(df.columns)}")
    keep_cols = []

    # Genre -> multi-label binarizer
    helpers.genre_mlb = MultiLabelBinarizer()
    genres_matrix = helpers.genre_mlb.fit_transform(df["Genres"])
    genres_df = pd.DataFrame(genres_matrix, columns=helpers.genre_mlb.classes_).add_prefix("Genre_")
    keep_cols += list(genres_df.columns)
    df = pd.concat([df.drop(columns="Genres"), genres_df], axis=1)
    print(f"Applied MLB for genres {df.shape}")

    # Directing -> FeatureHasher
    helpers.directing_hasher = FeatureHasher(n_features=256, input_type="string")
    directing_matrix = helpers.directing_hasher.fit_transform(df["Directing"])
    directing_df = pd.DataFrame(directing_matrix.toarray()).add_prefix("Directing_")
    keep_cols += list(directing_df.columns)
    df = pd.concat([df.drop(columns="Directing"), directing_df], axis=1)
    print(f"Applied hasher for directing {df.shape}")

    # Producing -> FeatureHasher
    helpers.producing_hasher = FeatureHasher(n_features=256, input_type="string")
    producing_matrix = helpers.producing_hasher.fit_transform(df["Producing"])
    producing_df = pd.DataFrame(producing_matrix.toarray()).add_prefix("Producing_")
    keep_cols += list(producing_df.columns)
    df = pd.concat([df.drop(columns="Producing"), producing_df], axis=1)
    print(f"Applied hasher for producing {df.shape}")

    # Writing -> FeatureHasher
    helpers.writing_hasher = FeatureHasher(n_features=256, input_type="string")
    writing_matrix = helpers.writing_hasher.fit_transform(df["Writing"])
    writing_df = pd.DataFrame(writing_matrix.toarray()).add_prefix("Writing_")
    keep_cols += list(writing_df.columns)
    df = pd.concat([df.drop(columns="Writing"), writing_df], axis=1)
    print(f"Applied hasher for writing {df.shape}")

    # Cast -> FeatureHasher
    helpers.cast_hasher = FeatureHasher(n_features=256, input_type="string")
    cast_matrix = helpers.cast_hasher.fit_transform(df["Cast"])
    cast_df = pd.DataFrame(cast_matrix.toarray()).add_prefix("Cast_")
    keep_cols += list(cast_df.columns)
    df = pd.concat([df.drop(columns="Cast"), cast_df], axis=1)
    print(f"Applied hasher for cast {df.shape}")

    # Keywords -> FeatureHasher
    helpers.keywords_hasher = FeatureHasher(n_features=256, input_type="string")
    keywords_matrix = helpers.keywords_hasher.fit_transform(df["Keywords"])
    keywords_df = pd.DataFrame(keywords_matrix.toarray()).add_prefix("Keyword_")
    keep_cols += list(keywords_df.columns)
    df = pd.concat([df.drop(columns="Keywords"), keywords_df], axis=1)
    print(f"Applied hasher for keywords {df.shape}")

    # Studio -> FeatureHasher
    helpers.studio_hasher = FeatureHasher(n_features=256, input_type="string")
    studio_matrix = helpers.studio_hasher.fit_transform(df["Studios"])
    studio_df = pd.DataFrame(studio_matrix.toarray()).add_prefix("Studios_")
    keep_cols += list(studio_df.columns)
    df = pd.concat([df.drop(columns="Studios"), studio_df], axis=1)
    print(f"Applied hasher for studios {df.shape}")

    # Rating -> OneHotEncoder
    helpers.rating_onehot = OneHotEncoder(dtype=np.int, categories="auto", sparse=False, handle_unknown="ignore")
    rating_matrix = helpers.rating_onehot.fit_transform(df["Rating"].values.reshape(-1, 1))
    rating_df = pd.DataFrame(rating_matrix).add_prefix("Rating_")
    keep_cols += list(rating_df.columns)
    df = pd.concat([df.drop(columns="Rating"), rating_df], axis=1)
    print(f"Applied one-hot encoder for rating {df.shape}")

    # # Date -> month and day one-hot
    helpers.month_onehot = OneHotEncoder(dtype=np.int, categories="auto", sparse=False, handle_unknown="ignore")
    month_matrix = helpers.month_onehot.fit_transform(df["Date"].apply(lambda d: d.month).values.reshape(-1, 1))
    helpers.day_onehot = OneHotEncoder(dtype=np.int, categories="auto", sparse=False, handle_unknown="ignore")
    day_matrix = helpers.day_onehot.fit_transform(df["Date"].apply(lambda d: d.day).values.reshape(-1, 1))

    month_df = pd.DataFrame(month_matrix).add_prefix("Month_")
    day_df = pd.DataFrame(day_matrix).add_prefix("Day_")
    keep_cols += list(month_df.columns) + list(day_df.columns)
    df = pd.concat([df.drop(columns="Date"), month_df, day_df], axis=1)
    print(f"Applied one-hot encoder for month and day {df.shape}")

    keep_cols += ["Budget", "Runtime", "Opening"]
    drop_cols = set(df.columns) - set(keep_cols)
    if drop_cols:
        print(f"Dropping non-feature columns: {drop_cols}")
        df = df.drop(columns=drop_cols)
        print(f"Final shape: {df.shape}")

    print("Writing output files...")
    df.to_pickle(FEATURES_PICKLE)
    print(f"{FEATURES_PICKLE} done")

    pd.to_pickle(helpers, TRAINING_HELPERS_PICKLE)
    print(f"{TRAINING_HELPERS_PICKLE} done")
    print(f"create_features_from_df: {time.time() - start:.1f}s")


def train_nn_model() -> None:
    """ Configure and train the neural net model.  Save the model and scalers for loading up in the app to use for
    predictions later.  Also save the separate test and train data sets as their own files. """
    start = time.time()
    helpers = ScalingHelpers()

    print(f"Reading {FEATURES_PICKLE}...")
    df = pd.read_pickle(FEATURES_PICKLE)
    print("Done.")

    target = df["Opening"]
    data = df.drop(columns=["Opening"])

    X_train, X_test, y_train, y_test = train_test_split(data, target, random_state=42)
    print(f"Train/test split --> train x={X_train.shape}/y={y_train.shape}, test x={X_test.shape}/y={y_test.shape}")

    helpers.x_scaler = MinMaxScaler().fit(X_train)
    helpers.y_scaler = MinMaxScaler().fit(y_train.values.reshape(-1, 1))

    X_train = helpers.x_scaler.transform(X_train)
    X_test = helpers.x_scaler.transform(X_test)
    y_train = helpers.y_scaler.transform(y_train.values.reshape(-1, 1))
    y_test = helpers.y_scaler.transform(y_test.values.reshape(-1, 1))

    print("Writing data files...")
    pd.to_pickle(helpers, NN_HELPERS_PICKLE)
    pd.to_pickle((X_train, y_train), NN_TRAIN_DATA_PICKLE)
    pd.to_pickle((X_test, y_test), NN_TEST_DATA_PICKLE)

    nn_model = Sequential()
    nn_model.add(Dense(units=1500, input_dim=int(X_test.shape[1]), activation='relu'))
    nn_model.add(Dense(units=800, activation='relu'))
    nn_model.add(Dense(units=300, activation='relu'))
    nn_model.add(Dense(units=1, activation='linear'))
    print(nn_model.summary())

    nn_model.compile(loss='mse', optimizer='adam', metrics=['mse', 'mae'])
    history = nn_model.fit(
        X_train,
        y_train,
        validation_data=(X_test, y_test),
        epochs=50,
        shuffle=False,
        verbose=2
    )
    pd.to_pickle(history, "Resources/nn_model_fit_history.pickle.gz")

    print(nn_model.evaluate(X_test, y_test, verbose=2))
    print(f"Saving model to {SEQUENTIAL_NN_MODEL_H5}")
    nn_model.save(SEQUENTIAL_NN_MODEL_H5)
    print(f"train_nn_model: {time.time() - start:.1f}")


def print_column_groups():
    """ Print out the column names in the features dataframe, grouping numbered columns together. """
    data = pd.read_pickle(FEATURES_PICKLE)
    prev_col = None
    count = 0
    for c in data.columns:
        cg = str(c).split("_")[0]
        if cg != prev_col:
            if prev_col:
                print(f"{prev_col} => {count}")
            prev_col = cg
            count = 0
        count += 1
    else:
        print(f"{prev_col} => {count}")


if __name__ == "__main__":
    # save_box_office_mojo_csv()
    # ~12 minutes
    # get_tmdb_ids()
    # ~20? minutes
    # get_tmdb_json()
    # parse_json_responses()
    create_features_from_merged_df()
    # ~2 minutes
    train_nn_model()
    print_column_groups()
