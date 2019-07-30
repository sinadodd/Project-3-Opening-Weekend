from flask import Flask, render_template, redirect
import app.js

# Create an instance of Flask
app = Flask(__name__)

# Route to render index.html template
@app.route("/")
def home():

    # Return template and data
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
