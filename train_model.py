import multiprocessing
import time
from multiprocessing import Lock

import numpy as np
import pandas as pd
from keras import Sequential
from keras.layers import Dense
from sklearn.feature_extraction import FeatureHasher
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, MinMaxScaler

from tmdb_api import load_tmdb_data_by_title

# Important filenames
TRAINING_HELPERS_PICKLE = "Resources/03_helpers.pickle.gz"
BOX_OFFICE_MOJO_XLS = "Resources/openingweekend_boxofficemojo.xlsx"
OPENINGWEEKEND_PICKLE = "Resources/openingweekend.pickle.gz"
MERGED_PICKLE = "Resources/02_data_after_API_calls.pickle.gz"
MERGE_ERRORS_PICKLE = "Resources/02_merge_errors.pickle.gz"
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


global total_rows, processed_rows, start, report, error_count, lock, seen_titles, seen_ids, out_cols
seen_titles = set()
seen_ids = set()
total_rows = 0
processed_rows = 0
start = 0
report = 0
error_count = 0
lock = Lock()
out_cols = []


def process_chunk(df_chunk: pd.DataFrame) -> pd.DataFrame:
    """ Process a chunk of the split Box Office Mojo data, merging in TMDB API data. """
    global total_rows, processed_rows, start, report, error_count, lock, seen_ids, seen_titles, out_cols
    out_data = []
    for title, studio, opening, theaters, release_date in df_chunk.itertuples(index=False):
        with lock:
            processed_rows += 1
            t = time.time()
            if t > report:
                elapsed = t - start
                rate = processed_rows / elapsed
                print(f"Processed {processed_rows}/{total_rows} in {elapsed:.1f}s ({rate:.2f}/s) - "
                      f"{error_count} errors")
                report += 5

        errors = []
        (tmdb_data, error) = load_tmdb_data_by_title(title, release_date.year)
        if error:
            errors.append(error)

        row = [title, studio, opening, theaters, release_date,
               tmdb_data.tmdb_id, tmdb_data.budget, tmdb_data.runtime,
               tmdb_data.genres, tmdb_data.directors, tmdb_data.producers, tmdb_data.writers,
               tmdb_data.rating]

        with lock:
            if title in seen_titles:
                msg = f"Duplicate title {title}"
                errors.append(msg)
                print(msg)
                seen_titles.add(title)

            if tmdb_data.tmdb_id in seen_ids:
                msg = f"Duplicate TMDB ID {tmdb_data.tmdb_id}"
                errors.append(msg)
                print(msg)
            if tmdb_data.tmdb_id:
                seen_ids.add(tmdb_data.tmdb_id)

        e = "; ".join(errors) or None
        row.append(e)
        if e:
            with lock:
                error_count += 1

        out_data.append(row)

    return pd.DataFrame(out_data, columns=out_cols)


def merge_tmdb_api_data() -> None:
    """ Load the Box Office Mojo data and merge it with TMDB data via the TMDB API.
    Save the result as a gzipped pickle file. """
    print(f"Loading pickle file {OPENINGWEEKEND_PICKLE}...")
    bom_df = pd.read_pickle(OPENINGWEEKEND_PICKLE)
    print("Done.")

    global total_rows, processed_rows, start, report, error_count, lock, out_cols
    out_cols = [
        "Title", "Studio", "Opening", "Theaters", "Date",
        "Movie ID", "Budget", "Runtime",
        "Genres", "Directing", "Producing", "Writing",
        "Rating",
        "Drop Reason"
    ]

    total_rows = len(bom_df.index)
    processed_rows = 0
    start = time.time()
    report = start + 5
    error_count = 0
    lock = Lock()

    num_partitions = 1 # Rate-limiting actually makes parallel processing slower...
    df_split = np.array_split(bom_df, num_partitions)
    print(f"Split for parallel processing: {[d.shape for d in df_split]}")
    pool = multiprocessing.Pool(num_partitions)
    print(f"Start parallel processing...")
    df = pd.concat(pool.map(process_chunk, df_split))
    pool.close()
    print(f"Wait for jobs to complete...")
    pool.join()
    print(f"Done.")

    print(f"Combined data {df.shape}")
    print("Writing output files...")
    df.to_pickle(MERGED_PICKLE)
    print(f"{MERGED_PICKLE} done")

    df[df["Drop Reason"].notnull()].to_pickle(MERGE_ERRORS_PICKLE)
    print(f"{MERGE_ERRORS_PICKLE} done")


class TrainingHelpers:
    """ Holder class for various transformation objects we need to use on prediction inputs. Put these
    all in one place so we can pickle this object and unpickle it in the app easily. """
    genre_mlb: MultiLabelBinarizer
    directing_hasher: FeatureHasher
    producing_hasher: FeatureHasher
    writing_hasher: FeatureHasher
    studio_onehot: OneHotEncoder
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

    # Studio -> OneHotEncoder
    helpers.studio_onehot = OneHotEncoder(dtype=np.int, categories="auto", sparse=False)
    studio_matrix = helpers.studio_onehot.fit_transform(df["Studio"].values.reshape(-1, 1))
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
    data = df.drop(columns=["Opening", "Movie ID", "Title"])
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

    nn_model.compile(loss='mse', optimizer='adam', metrics=['mse','mae'])
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
    # This step takes ~50 minutes to complete due to API rate limiting
    # merge_tmdb_api_data()
    create_features_from_merged_df()
    # This step takes a few minutes (~5) to complete currently
    train_nn_model()
    print_column_groups()
