# 🚚 CVRP Solver — Interactive Capacitated Vehicle Routing Problem Solver

A full-stack web application for solving the **Capacitated Vehicle Routing Problem (CVRP)** with an interactive Google Maps interface. Users place a depot and customer locations on the map, set demands and vehicle capacity, then visualize optimized delivery routes computed by one of five selectable algorithms.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-lightgrey?logo=flask)
![Google Maps](https://img.shields.io/badge/Google%20Maps-API-green?logo=googlemaps)
![OR--Tools](https://img.shields.io/badge/OR--Tools-9.12-orange)


---

## ✨ Features

- **Interactive Map UI** — Click on the map or search an address to place a depot and up to 9 customer locations.
- **Real-World Distances** — Uses the Google Distance Matrix API to build accurate road-distance matrices.
- **5 Solving Algorithms** — Choose from:
  | Algorithm | Type | Description |
  |---|---|---|
  | **Nearest Neighbour** | Greedy heuristic | Iteratively visits the closest feasible customer |
  | **Clarke-Wright Savings** | Savings heuristic | Merges routes based on distance savings |
  | **Google OR-Tools** | Metaheuristic (Path Cheapest Arc) | Google's constraint-based optimization solver |
  | **Ant Colony Optimization** | Metaheuristic | Bio-inspired pheromone-based route construction |
  | **Exact (ILP)** | Optimal (Integer Linear Programming) | Single-commodity flow formulation solved with PuLP/CBC |
- **Route Visualization** — Solved routes are drawn on the map with color-coded driving directions.
- **Solution Summary Popup** — Displays each route and total distance in km.
- **Responsive Design** — Works on desktop and mobile screens.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, Flask |
| **Frontend** | HTML, CSS, JavaScript |
| **Maps & Geocoding** | Google Maps JavaScript API, Distance Matrix API |
| **Optimization** | Google OR-Tools, PuLP (CBC solver) |
| **Deployment** | Gunicorn, Render |

---

## 📁 Project Structure

```
CVRP_App/
├── app.py                      # Flask server & API endpoint
├── Procfile                    # Gunicorn config for deployment
├── requirements.txt            # Python dependencies
├── cvrp_algorithms/
│   ├── Algoritmi.py            # All 5 CVRP algorithm implementations
│   └── Slika.py                # Matplotlib visualization (for local testing)
├── static/
│   ├── main.js                 # Map interaction, route drawing, UI logic
│   └── styles.css              # Responsive styling
└── templates/
    └── index.html              # Main page template
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- A **Google Cloud** project with the following APIs enabled:
  - Maps JavaScript API
  - Distance Matrix API
  - Geocoding API

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sarmaguy/CVRP_App.git
   cd CVRP_App
   ```

2. **Create a virtual environment & install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set your Google Maps API key**

   Create a `config.py` file in the project root:
   ```python
   GOOGLE_MAPS_API_KEY = "YOUR_API_KEY_HERE"
   ```
   Or set the environment variable:
   ```bash
   export GOOGLE_MAPS_API_KEY="YOUR_API_KEY_HERE"
   ```

4. **Run the app**
   ```bash
   python app.py
   ```
   Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 📖 How to Use

1. **Set the Depot** — Click on the map (or type an address) to place the depot (shown as a black "D" marker).
2. **Add Customers** — Click on additional locations and enter each customer's demand.
3. **Set Truck Capacity** — Enter the vehicle capacity in the input field.
4. **Choose an Algorithm** — Select one of the five algorithms from the selector bar.
5. **Solve** — Click **Solve** to compute routes. The optimized routes are drawn on the map and a popup shows the route breakdown and total distance.
6. **Reset** — Click **Reset** to clear all markers and routes.

---

## 🧮 Algorithm Details

### Nearest Neighbour
A greedy constructive heuristic that always visits the nearest unvisited, capacity-feasible customer. Fast but generally suboptimal.

### Clarke-Wright Savings
Starts with one route per customer, then iteratively merges route pairs that yield the highest distance saving while respecting capacity.

### Google OR-Tools
Uses Google's open-source OR-Tools library with a `PATH_CHEAPEST_ARC` first-solution strategy and built-in capacity constraints.

### Ant Colony Optimization
A population-based metaheuristic where artificial ants construct solutions guided by pheromone trails and distance heuristics over multiple iterations (default: 10 ants × 100 iterations).

### Exact (ILP)
Formulates the CVRP as an Integer Linear Program using a single-commodity flow model. Solved to optimality with the PuLP/CBC solver. Best for small instances.

---

## 🌐 Deployment

The app is deployment-ready for **Render** (or any platform supporting Gunicorn):

```
web: gunicorn app:app
```

Set the `GOOGLE_MAPS_API_KEY` environment variable in your hosting platform's dashboard.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
