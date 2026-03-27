import json
import os

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Load the city-level data from JSON file
data_file = os.path.join("data", "temperature_data_city.json")
with open(data_file) as f:
    city_data = json.load(f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def get_data():
    year = request.args.get("year")
    if not year:
        return jsonify({"error": "Please provide 'year' parameter."}), 400

    # Return data only for the specified year
    if year in city_data:
        return jsonify(city_data[year])

    return jsonify({"error": "Data not found for specified year."}), 404


if __name__ == "__main__":
    app.run(debug=True)
