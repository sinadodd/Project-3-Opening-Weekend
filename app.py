import traceback

import predict_input
import tmdb_api

from flask import Flask, render_template, jsonify

# Create an instance of Flask
app = Flask(__name__, static_url_path="")
predict_input.init()

# Route to render index.html template
@app.route("/")
def home():
    # Return template and data
    return render_template("index.html")


@app.route("/upcoming")
def upcoming():
    return jsonify([s.__dict__ for s in tmdb_api.get_upcoming()])


@app.route("/predict/<int:tmdb_id>")
def predict(tmdb_id):
    (s, err, json) = tmdb_api.load_from_tmdb(tmdb_id)

    s.actual_opening = None
    try:
        s.actual_opening = predict_input.get_actual_opening(tmdb_id)
    except KeyError:
        pass

    s.predicted_opening = None
    try:
        s.predicted_opening = float(predict_input.predict_for_input(s))
    except Exception as e:
        traceback.print_exc()

    return jsonify(s.__dict__)


if __name__ == "__main__":
    app.run()
