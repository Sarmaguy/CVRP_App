from flask import Flask, render_template, request, jsonify
from cvrp_algorithms.Algoritmi import clarke_wright,nearest_neighbor  # adjust import
import requests
import os
from config import GOOGLE_MAPS_API_KEY

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', api_key=GOOGLE_MAPS_API_KEY)

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    locations = data['locations']  # list of [lat, lng]
    demands = data['demands']
    capacity = data['capacity']

    # Request distance matrix from Google
    origin_dest = '|'.join([f"{lat},{lng}" for lat, lng in locations])
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        'origins': origin_dest,
        'destinations': origin_dest,
        'key': GOOGLE_MAPS_API_KEY
    }
    response = requests.get(url, params=params)
    matrix_data = response.json()

    distance_matrix = [
        [element['distance']['value'] for element in row['elements']]
        for row in matrix_data['rows']
    ]

    # Solve CVRP
    #routes = #

    return jsonify(routes)
