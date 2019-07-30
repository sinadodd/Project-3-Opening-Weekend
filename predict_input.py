import numpy
import pandas as pd
from tensorflow.python.keras.models import load_model, Sequential

from tmdb_api import InputSample, load_from_tmdb
from train_model import TrainingHelpers, ScalingHelpers, NN_HELPERS_PICKLE, TRAINING_HELPERS_PICKLE, \
    SEQUENTIAL_NN_MODEL_H5

nn_model: Sequential = load_model(SEQUENTIAL_NN_MODEL_H5)

training_helpers: TrainingHelpers = pd.read_pickle(TRAINING_HELPERS_PICKLE)
scaling_helpers: ScalingHelpers = pd.read_pickle(NN_HELPERS_PICKLE)


def predict_for_input(i: InputSample) -> float:

    # Theaters => 1 int
    # Budget => 1 int
    # Runtime => 1 float
    features = [i.theaters, i.budget, i.runtime]

    # Genre => onehot / multi-label binarizer
    features.extend(training_helpers.genre_mlb.transform([i.genres])[0])
    # Director => hasher
    features.extend(training_helpers.directing_hasher.transform([i.directors]).toarray()[0])
    # Producer => hasher
    features.extend(training_helpers.producing_hasher.transform([i.producers]).toarray()[0])
    # Writer => hashser
    features.extend(training_helpers.writing_hasher.transform([i.writers]).toarray()[0])
    # Studio => onehot
    features.extend(training_helpers.studio_onehot.transform([[i.studio]])[0])
    # Rating => onehot
    features.extend(training_helpers.rating_onehot.transform([[i.rating]])[0])
    # Month => onehot
    features.extend(training_helpers.month_onehot.transform([[i.month]])[0])
    # Day => onehot
    features.extend(training_helpers.day_onehot.transform([[i.day]])[0])

    features = scaling_helpers.x_scaler.transform([features])[0]

    prediction = nn_model.predict(numpy.array(features).reshape(1, -1))

    return scaling_helpers.y_scaler.inverse_transform(prediction)[0][0]


if __name__ == "__main__":
    # Test movie: The Lion King 2019 - 420818
    lion_king, errors = load_from_tmdb(420818)
    assert errors is None
    print(predict_for_input(lion_king))
