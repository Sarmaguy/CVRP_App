from flask import Flask, render_template, request, jsonify
from cvrp_algorithms.Algoritmi import clarke_wright,nearest_neighbor,google,ant_colony,exact
import requests
from config import GOOGLE_MAPS_API_KEY


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', api_key=GOOGLE_MAPS_API_KEY)

@app.route('/solve', methods=['POST'])
def solve():
    try:
        data = request.json
        locations = data['locations']
        demands   = data['demands']
        capacity  = data['capacity']
        algorithm = data['algorithm']
        print("Received data:", data)

        od = '|'.join(f"{lat},{lng}" for lat, lng in locations)
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            params={'origins': od, 'destinations': od, 'key': GOOGLE_MAPS_API_KEY}
        )
        matrix_data = resp.json()
        #print("tu1")
        if matrix_data.get('status') != 'OK':
            return jsonify({'error': 'Distance Matrix API error', 'details': matrix_data}), 500
        #print("tu2")
        distance_matrix = []
        for i, row in enumerate(matrix_data['rows']):
            dm_row = []
            for j, elt in enumerate(row['elements']):
                if elt.get('status') == 'OK':
                    dm_row.append(elt['distance']['value'])
                else:
                    dm_row.append(float('inf'))
            distance_matrix.append(dm_row)
        #print("tu3")
        distance = 0
        if algorithm == 'clarke-wright':
            routes,distance = clarke_wright(distance_matrix, demands, capacity)
        elif algorithm == 'nearest':
            routes, distance = nearest_neighbor(distance_matrix, demands, capacity)
        elif algorithm == 'google':
            routes, distance = google(distance_matrix, demands, capacity)
        elif algorithm == 'ant-colony':
            routes, distance = ant_colony(distance_matrix, demands, capacity)
        elif algorithm == 'exact':
            routes, distance = exact(distance_matrix, demands, capacity)
        else:
            return jsonify({'error': 'Invalid algorithm selected'}), 400

        print("Routes found:", routes)
        return jsonify(routes=routes, distance=distance)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error during solving:", str(e))
        return jsonify({'error': str(e)}), 500
