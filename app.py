import pandas as pd
from flask import Flask, render_template, jsonify

# import predict_input
import tmdb_api
import train_model

# Create an instance of Flask
app = Flask(__name__)

known_movies_df: pd.DataFrame = pd.read_pickle(train_model.OPENINGWEEKEND_WITH_TMDB_IDS_PICKLE)
known_movies_df.set_index("Movie ID", inplace=True, drop=False)

# Route to render index.html template
@app.route("/")
def home():
    # Return template and data
    return render_template("index.html")


@app.route("/upcoming")
def upcoming():
    return jsonify([s.__dict__ for s in tmdb_api.get_upcoming()])


@app.route("/info/<int:tmdb_id>")
def info(tmdb_id):
    (s, err, json) = tmdb_api.load_from_tmdb(tmdb_id)
    s.predicted_opening = None
    s.actual_opening = None
    try:
        s.actual_opening = float(known_movies_df.loc[tmdb_id, "Opening"])
    except KeyError:
        pass

    return jsonify(s.__dict__)


@app.route("/predict/<int:tmdb_id>")
def predict(tmdb_id):
    (s, err, json) = tmdb_api.load_from_tmdb(tmdb_id)

    s.actual_opening = None
    # try:
    #     s.actual_opening = int(known_movies_df.loc[tmdb_id, "Opening"])
    # except KeyError:
    #     pass

    s.predicted_opening = None
    # s.predicted_opening = float(predict_input.predict_for_input(s))

    return jsonify(s.__dict__)


if __name__ == "__main__":
    app.run(debug=True)
