import numpy
import pandas as pd
from tensorflow.python.keras.models import load_model, Sequential

import tmdb_api
import train_model

nn_model: Sequential = load_model(train_model.SEQUENTIAL_NN_MODEL_H5)

training_helpers: train_model.TrainingHelpers = pd.read_pickle(train_model.TRAINING_HELPERS_PICKLE)
scaling_helpers: train_model.ScalingHelpers = pd.read_pickle(train_model.NN_HELPERS_PICKLE)


def predict_for_input(i: tmdb_api.InputSample) -> float:

    # Budget => 1 int
    # Runtime => 1 float
    features = [i.budget, i.runtime]

    # Genre => onehot / multi-label binarizer
    features.extend(training_helpers.genre_mlb.transform([
        [g for g in i.genres if g in training_helpers.genre_mlb.classes_]
    ])[0])
    # Director => hasher
    features.extend(training_helpers.directing_hasher.transform([i.directors]).toarray()[0])
    # Producer => hasher
    features.extend(training_helpers.producing_hasher.transform([i.producers]).toarray()[0])
    # Writer => hashser
    features.extend(training_helpers.writing_hasher.transform([i.writers]).toarray()[0])
    # Studio => multi-label binarizer
    features.extend(training_helpers.studio_mlb.transform([
        [s for s in i.studios if s in training_helpers.studio_mlb.classes_]
    ])[0])
    # Rating => onehot
    features.extend(training_helpers.rating_onehot.transform([
        [i.rating] if i.rating in training_helpers.rating_onehot.categories_ else []
    ])[0])
    # Month => onehot
    features.extend(training_helpers.month_onehot.transform([
        [i.month] if i.month in range(1, 13) else []
    ])[0])
    # Day => onehot
    features.extend(training_helpers.day_onehot.transform([
        [i.day] if i.day in range(1, 32) else []
    ])[0])

    features = scaling_helpers.x_scaler.transform([features])[0]

    prediction = nn_model.predict(numpy.array(features).reshape(1, -1))

    return scaling_helpers.y_scaler.inverse_transform(prediction)[0][0]


if __name__ == "__main__":
    # Test movie: The Lion King 2019 - 420818
    lion_king, errors, _ = tmdb_api.load_from_tmdb(420818)
    assert errors is None
    print(predict_for_input(lion_king))
