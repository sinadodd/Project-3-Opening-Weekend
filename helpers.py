from sklearn.feature_extraction import FeatureHasher
from sklearn.preprocessing import MinMaxScaler, MultiLabelBinarizer, OneHotEncoder


class ScalingHelpers:
    """ Helpers for the NN training process.  Keep these in one object so we can pickle it easily. """
    x_scaler: MinMaxScaler
    y_scaler: MinMaxScaler


class TrainingHelpers:
    """ Holder class for various transformation objects we need to use on prediction inputs. Put these
    all in one place so we can pickle this object and unpickle it in the app easily. """
    genre_mlb: MultiLabelBinarizer
    directing_hasher: FeatureHasher
    producing_hasher: FeatureHasher
    writing_hasher: FeatureHasher
    cast_hasher: FeatureHasher
    keywords_hasher: FeatureHasher
    studio_hasher: FeatureHasher
    rating_onehot: OneHotEncoder
    month_onehot: OneHotEncoder
    day_onehot: OneHotEncoder