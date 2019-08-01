from typing import Optional

import numpy
import tensorflow as tf
from keras.backend import set_session
from tensorflow import Graph, Session
from keras.models import load_model, Sequential

import tmdb_api
from train_model import SEQUENTIAL_NN_MODEL_H5, OPENINGWEEKEND_WITH_TMDB_IDS_PICKLE, TRAINING_HELPERS_PICKLE, NN_HELPERS_PICKLE
from helpers import ScalingHelpers, TrainingHelpers
import pandas as pd

known_movies_df: Optional[pd.DataFrame] = None
tf_session: Session = tf.Session()
tf_graph: Graph = tf.get_default_graph()
set_session(tf_session)
nn_model: Optional[Sequential] = load_model(SEQUENTIAL_NN_MODEL_H5)
training_helpers: Optional[TrainingHelpers] = None
scaling_helpers: Optional[ScalingHelpers] = None


def predict_for_input(i: tmdb_api.InputSample) -> float:

    # Budget => 1 int
    # Runtime => 1 float
    features = [i.budget, i.runtime]

    # Genre => onehot / multi-label binarizer
    features.extend(training_helpers.genre_mlb.transform([i.genres])[0])
    # Director => hasher
    features.extend(training_helpers.directing_hasher.transform([i.directors]).toarray()[0])
    # Producer => hasher
    features.extend(training_helpers.producing_hasher.transform([i.producers]).toarray()[0])
    # Writer => hashser
    features.extend(training_helpers.writing_hasher.transform([i.writers]).toarray()[0])
    # Keywords => hasher
    features.extend(training_helpers.keywords_hasher.transform([i.keywords]).toarray()[0])
    # Studio => hasher
    features.extend(training_helpers.studio_hasher.transform([i.studios]).toarray()[0])
    # Cast => hasher
    features.extend(training_helpers.cast_hasher.transform([i.cast]).toarray()[0])
    # Rating => onehot
    features.extend(training_helpers.rating_onehot.transform([[i.rating]])[0])
    # Month => onehot
    features.extend(training_helpers.month_onehot.transform([[i.month]])[0])
    # Day => onehot
    features.extend(training_helpers.day_onehot.transform([[i.day]])[0])

    features = scaling_helpers.x_scaler.transform([features])[0]

    global tf_session, tf_graph
    with tf_graph.as_default():
        set_session(tf_session)
        prediction = nn_model.predict(numpy.array(features).reshape(1, -1))

    return scaling_helpers.y_scaler.inverse_transform(prediction)[0][0]


def get_actual_opening(tmdb_id):
    try:
        return known_movies_df[tmdb_id, "Opening"]
    except KeyError:
        return None


def init():
    global known_movies_df, training_helpers, scaling_helpers

    known_movies_df = pd.read_pickle(OPENINGWEEKEND_WITH_TMDB_IDS_PICKLE)
    known_movies_df.set_index("ID", drop=False, inplace=True)
    training_helpers = pd.read_pickle(TRAINING_HELPERS_PICKLE)
    scaling_helpers = pd.read_pickle(NN_HELPERS_PICKLE)


if __name__ == "__main__":
    init()
    # Test movie: The Lion King 2019 - 420818
    lion_king, errors, _ = tmdb_api.load_from_tmdb(420818)
    assert errors is None
    print(predict_for_input(lion_king))
