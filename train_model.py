import time
import traceback

import numpy as np
import pandas as pd
from keras import Sequential
from keras.layers import Dense
from requests import HTTPError, Response
from sklearn.feature_extraction import FeatureHasher
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, MinMaxScaler

from tmdb_api import get_tmdb_id_from_title, load_from_tmdb

# Important filenames
TRAINING_HELPERS_PICKLE = "Resources/03_helpers.pickle.gz"
BOX_OFFICE_MOJO_XLS = "Resources/openingweekend_boxofficemojo.xlsx"
OPENINGWEEKEND_PICKLE = "Resources/openingweekend.pickle.gz"
OPENINGWEEKEND_WITH_TMDB_IDS_PICKLE = "Resources/openingweekend_ids.pickle.gz"
MERGED_PICKLE = "Resources/02_data_after_API_calls.pickle.gz"
MERGE_ERRORS_ID_PICKLE = "Resources/merge_errors_id.pickle.gz"
MERGE_ERRORS_INFO_PICKLE = "Resources/merge_errors_info.pickle.gz"
WITH_FEATURES_PICKLE = "Resources/03_new_df.pickle.gz"
SEQUENTIAL_NN_MODEL_H5 = "Resources/sequential_nn_model.h5"
NN_HELPERS_PICKLE = "Resources/nn_helpers.pickle.gz"
NN_TRAIN_DATA_PICKLE = "Resources/nn_train_data.pickle.gz"
NN_TEST_DATA_PICKLE = "Resources/nn_test_data.pickle.gz"


def save_box_office_mojo_csv() -> None:
    """ Load the Box Office Mojo excel spreadsheet and rename/drop columns.
    Save the result as a gzipped pickle file. """
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


def get_tmdb_ids() -> None:
    """ Load the Box Office Mojo data and determine the TMDB ID for each entry.
    Save the result as a gzipped pickle file. """
    print(f"Loading pickle file {OPENINGWEEKEND_PICKLE}...")
    bom_df = pd.read_pickle(OPENINGWEEKEND_PICKLE)
    print("Done.")

    out_cols = [
        "Title", "Studio", "Opening", "Theaters", "Date",
        "Movie ID",
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
    for title, studio, opening, theaters, release_date in bom_df.itertuples(index=False):
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

        out_data.append([
            title, studio, opening, theaters, release_date,
            tmdb_id,
            "; ".join(errors) or None
        ])

    with_tmdb_ids_df = pd.DataFrame(out_data, columns=out_cols)

    print(f"Data with IDs: {with_tmdb_ids_df.shape} / errors: {with_tmdb_ids_df['Drop Reason'].count()}")
    print("Writing output files...")
    with_tmdb_ids_df[with_tmdb_ids_df["Drop Reason"].isnull()].to_pickle(OPENINGWEEKEND_WITH_TMDB_IDS_PICKLE)
    with_tmdb_ids_df[with_tmdb_ids_df["Drop Reason"].notnull()].to_pickle(MERGE_ERRORS_ID_PICKLE)
    print("Done.")


def get_tmdb_details() -> None:
    """ Load the JSON details for each movie we have a TMDB ID for.
    Save the result as a gzipped pickle file. """
    print(f"Loading pickle file {OPENINGWEEKEND_WITH_TMDB_IDS_PICKLE}...")
    with_tmdb_ids_df = pd.read_pickle(OPENINGWEEKEND_WITH_TMDB_IDS_PICKLE)
    print("Done.")

    out_cols = [
        "Title", "Studio", "Opening", "Theaters", "Date",
        "Movie ID",
        "Drop Reason", "JSON",
        "Budget", "Runtime",
        "Genres", "Directing", "Producing", "Writing",
        "Rating", "Keywords", "Studios",
        "Raw Data",
    ]

    total_rows = len(with_tmdb_ids_df.index)

    processed_rows = 0
    start = time.time()
    report = start + 5
    error_count = 0

    out_data = []
    for title, studio, opening, theaters, release_date, tmdb_id, _ in with_tmdb_ids_df.itertuples(index=False):
        processed_rows += 1
        t = time.time()
        if t > report:
            elapsed = t - start
            rate = processed_rows / elapsed
            print(f"Processed {processed_rows}/{total_rows} in {elapsed:.1f}s ({rate:.2f}/s) - "
                  f"{error_count} errors")
            report += 5

        (tmdb_data, error, json_resp) = load_from_tmdb(tmdb_id)

        out_data.append([
            title, studio, opening, theaters, release_date,
            tmdb_id,
            error, json_resp,
            tmdb_data.budget, tmdb_data.runtime,
            tmdb_data.genres, tmdb_data.directors, tmdb_data.producers, tmdb_data.writers,
            tmdb_data.rating, tmdb_data.keywords, tmdb_data.studios,
            tmdb_data
        ])
        if error:
            error_count += 1

    df = pd.DataFrame(out_data, columns=out_cols)

    print(f"Combined data {df.shape} / errors: {df['Drop Reason'].count()}")
    print("Writing output files...")
    df[df["Drop Reason"].isnull()].to_pickle(MERGED_PICKLE)
    df[df["Drop Reason"].notnull()].to_pickle(MERGE_ERRORS_INFO_PICKLE)
    print(f"{MERGE_ERRORS_INFO_PICKLE} done")


class TrainingHelpers:
    """ Holder class for various transformation objects we need to use on prediction inputs. Put these
    all in one place so we can pickle this object and unpickle it in the app easily. """
    genre_mlb: MultiLabelBinarizer
    directing_hasher: FeatureHasher
    producing_hasher: FeatureHasher
    writing_hasher: FeatureHasher
    keywords_hasher: FeatureHasher
    studio_mlb: MultiLabelBinarizer
    rating_onehot: OneHotEncoder
    month_onehot: OneHotEncoder
    day_onehot: OneHotEncoder


def create_features_from_merged_df() -> None:
    """ Transform the combined input data into features useful for ML algorithms.
    Save the result as a gzipped pickle file. """
    helpers = TrainingHelpers()

    print(f"Loading {MERGED_PICKLE}...")
    df = pd.read_pickle(MERGED_PICKLE)
    print("Done.")

    print(f"Starting feature creation: {df.shape}")

    drop_count = df[df["Drop Reason"].notnull()].count()
    df = df[df["Drop Reason"].isnull()].drop(columns="Drop Reason")
    print(f"Dropping {drop_count} error rows; {df.shape}")

    df = df.dropna(axis='columns', how='all').dropna()
    df.reset_index(inplace=True, drop=True)
    print(f"Dropping na columns/rows; {df.shape}")

    # Genre -> multi-label binarizer
    helpers.genre_mlb = MultiLabelBinarizer()
    genres_matrix = helpers.genre_mlb.fit_transform(df["Genres"])
    genres_df = pd.DataFrame(genres_matrix, columns=helpers.genre_mlb.classes_).add_prefix("Genre_")
    df = pd.concat([df.drop(columns="Genres"), genres_df], axis=1)
    print(f"Applied MLB for genres {df.shape}")

    # Directing -> FeatureHasher
    helpers.directing_hasher = FeatureHasher(n_features=256, input_type="string")
    directing_matrix = helpers.directing_hasher.fit_transform(df["Directing"])
    directing_df = pd.DataFrame(directing_matrix.toarray()).add_prefix("Directing_")
    df = pd.concat([df.drop(columns="Directing"), directing_df], axis=1)
    print(f"Applied hasher for directing {df.shape}")

    # Producing -> FeatureHasher
    helpers.producing_hasher = FeatureHasher(n_features=256, input_type="string")
    producing_matrix = helpers.producing_hasher.fit_transform(df["Producing"])
    producing_df = pd.DataFrame(producing_matrix.toarray()).add_prefix("Producing_")
    df = pd.concat([df.drop(columns="Producing"), producing_df], axis=1)
    print(f"Applied hasher for producing {df.shape}")

    # Writing -> FeatureHasher
    helpers.writing_hasher = FeatureHasher(n_features=256, input_type="string")
    writing_matrix = helpers.writing_hasher.fit_transform(df["Writing"])
    writing_df = pd.DataFrame(writing_matrix.toarray()).add_prefix("Writing_")
    df = pd.concat([df.drop(columns="Writing"), writing_df], axis=1)
    print(f"Applied hasher for writing {df.shape}")

    # Keywords -> FeatureHasher
    helpers.keywords_hasher = FeatureHasher(n_features=256, input_type="string")
    keywords_matrix = helpers.keywords_hasher.fit_transform(df["Keywords"])
    keywords_df = pd.DataFrame(keywords_matrix.toarray()).add_prefix("Keyword_")
    df = pd.concat([df.drop(columns="Keywords"), keywords_df], axis=1)
    print(f"Applied hasher for keywords {df.shape}")

    # Studio -> MultiLabelBinarizer
    helpers.studio_mlb = MultiLabelBinarizer()
    studio_matrix = helpers.studio_mlb.fit_transform(df["Studio"].values.reshape(-1, 1))
    df = pd.concat([df.drop(columns="Studio"), pd.DataFrame(studio_matrix).add_prefix("Studio_")], axis=1)
    print(f"Applied one-hot encoder for studio {df.shape}")

    # Rating -> OneHotEncoder
    helpers.rating_onehot = OneHotEncoder(dtype=np.int, categories="auto", sparse=False)
    rating_matrix = helpers.rating_onehot.fit_transform(df["Rating"].values.reshape(-1, 1))
    df = pd.concat([df.drop(columns="Rating"), pd.DataFrame(rating_matrix).add_prefix("Rating_")], axis=1)
    print(f"Applied one-hot encoder for rating {df.shape}")

    # # Date -> month and day one-hot
    helpers.month_onehot = OneHotEncoder(dtype=np.int, categories="auto", sparse=False)
    month_matrix = helpers.month_onehot.fit_transform(df["Date"].apply(lambda d: d.month).values.reshape(-1, 1))
    helpers.day_onehot = OneHotEncoder(dtype=np.int, categories="auto", sparse=False)
    day_matrix = helpers.day_onehot.fit_transform(df["Date"].apply(lambda d: d.day).values.reshape(-1, 1))

    df = pd.concat([df.drop(columns="Date"),
                    pd.DataFrame(month_matrix).add_prefix("Month_"),
                    pd.DataFrame(day_matrix).add_prefix("Day_")],
                   axis=1)
    print(f"Applied one-hot encoder for month and day {df.shape}")

    print("Writing output files...")
    df.to_pickle(WITH_FEATURES_PICKLE)
    print(f"{WITH_FEATURES_PICKLE} done")

    pd.to_pickle(helpers, TRAINING_HELPERS_PICKLE)
    print(f"{TRAINING_HELPERS_PICKLE} done")


class ScalingHelpers:
    """ Helpers for the NN training process.  Keep these in one object so we can pickle it easily. """
    x_scaler: MinMaxScaler
    y_scaler: MinMaxScaler


def train_nn_model() -> None:
    """ Configure and train the neural net model.  Save the model and scalers for loading up in the app to use for
    predictions later.  Also save the separate test and train data sets as their own files. """
    helpers = ScalingHelpers()

    print(f"Reading {WITH_FEATURES_PICKLE}...")
    df = pd.read_pickle(WITH_FEATURES_PICKLE)
    print("Done.")

    target = df["Opening"]
    data = df.drop(columns=["Opening", "Movie ID", "Title", "Theaters", "Raw Data", "Studio", "JSON"])
    X_train, X_test, y_train, y_test = train_test_split(data, target, random_state=42)
    print(f"Train/test split --> train x={X_train.shape}/y={y_train.shape}, test x={X_test.shape}/y={y_test.shape}")

    helpers.x_scaler = MinMaxScaler().fit(X_train)
    helpers.y_scaler = MinMaxScaler().fit(y_train.values.reshape(-1, 1))

    X_train = helpers.x_scaler.transform(X_train)
    X_test = helpers.x_scaler.transform(X_test)
    y_train = helpers.y_scaler.transform(y_train.values.reshape(-1, 1))
    y_test = helpers.y_scaler.transform(y_test.values.reshape(-1, 1))

    nn_model = Sequential()
    nn_model.add(Dense(units=1500, input_dim=int(X_test.shape[1]), activation='relu'))
    nn_model.add(Dense(units=800, activation='relu'))
    nn_model.add(Dense(units=300, activation='relu'))
    nn_model.add(Dense(units=1, activation='linear'))
    print(nn_model.summary())

    nn_model.compile(loss='mse', optimizer='adam', metrics=['mse', 'mae'])
    nn_model.fit(
        X_train,
        y_train,
        epochs=100,
        shuffle=False,
        verbose=2
    )

    print(nn_model.evaluate(X_test, y_test, verbose=2))
    print(f"Saving model to {SEQUENTIAL_NN_MODEL_H5}")
    nn_model.save(SEQUENTIAL_NN_MODEL_H5)

    print("Writing data files...")
    pd.to_pickle(helpers, NN_HELPERS_PICKLE)
    pd.to_pickle((X_train, y_train), NN_TRAIN_DATA_PICKLE)
    pd.to_pickle((X_test, y_test), NN_TEST_DATA_PICKLE)


def print_column_groups():
    """ Print out the column names in the features dataframe, grouping numbered columns together. """
    data = pd.read_pickle(WITH_FEATURES_PICKLE)
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
    # ~7 minutes
    # get_tmdb_details()
    # create_features_from_merged_df()
    # ~5 minutesx
    train_nn_model()
    print_column_groups()
