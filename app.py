from flask import Flask, render_template, request, jsonify
from cvrp_algorithms.Algoritmi import clarke_wright,nearest_neighbor
import requests
from config import GOOGLE_MAPS_API_KEY

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', api_key=GOOGLE_MAPS_API_KEY)

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    locations = data['locations']
    demands   = data['demands']
    capacity  = data['capacity']

    # Build origins/destinations string
    od = '|'.join(f"{lat},{lng}" for lat, lng in locations)
    resp = requests.get(
        "https://maps.googleapis.com/maps/api/distancematrix/json",
        params={'origins': od, 'destinations': od, 'key': GOOGLE_MAPS_API_KEY}
    )
    matrix_data = resp.json()

    # Quick sanity check
    if matrix_data.get('status') != 'OK':
        return jsonify({'error': 'Distance Matrix API error', 'details': matrix_data}), 500

    distance_matrix = []
    for i, row in enumerate(matrix_data['rows']):
        dm_row = []
        for j, elt in enumerate(row['elements']):
            status = elt.get('status')
            if status == 'OK':
                dm_row.append(elt['distance']['value'])
            else:
                # you can choose to fail, or set a large cost:
                # return jsonify({'error': f'No route from {i} to {j}', 'status': status}), 400
                dm_row.append(float('inf'))
            # end if
        distance_matrix.append(dm_row)
    # end for

    # Solve the CVRP
    routes = nearest_neighbor(distance_matrix, demands, capacity)
    return jsonify(routes)
