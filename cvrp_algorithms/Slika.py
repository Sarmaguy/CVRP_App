import numpy as np
import matplotlib.pyplot as plt

def make_distance_matrix(coords):
    """Generates a distance matrix from coordinates."""
    n = len(coords)
    distance_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                distance_matrix[i][j] = np.linalg.norm(coords[i] - coords[j])
    return distance_matrix

# Fiksirane koordinate (isti seed za konzistentnost)
np.random.seed(43)
depot = np.array([50, 50])
customers = np.random.uniform(0, 100, size=(8, 2))
coords = np.vstack([depot, customers])  # Prva točka je depo (index 0)

distamatrix = make_distance_matrix(coords)
demands = np.random.randint(1, 10, size=(8,))  # Random demands for each customer
capacity = 10  # Kapacitet vozila

# Uvoz algoritama (pretpostavljamo da su implementirani u Algoritmi.py)
from Algoritmi import nearest_neighbor, clarke_wright,ant_colony,exact_cvrp_pulp
# Izvršavanje algoritama
nn_routes, nn_distance = nearest_neighbor(distamatrix, demands, capacity)
cw_routes, cw_distance = clarke_wright(distamatrix, demands, capacity)
ant_routes, ant_distance = ant_colony(distamatrix, demands, capacity)  
exact_routes, exact_distance = exact_cvrp_pulp(distamatrix, demands, capacity)

# Funkcija za crtanje ruta
def plot_routes(routes, coords, title, ax):
    for route in routes:
        path = [0] + route + [0]  # početak i kraj u depou
        color = np.random.rand(3,)
        for i in range(len(path) - 1):
            start = coords[path[i]]
            end = coords[path[i + 1]]
            ax.plot([start[0], end[0]], [start[1], end[1]], color=color, linewidth=2, alpha=0.7)
    # Točke
    ax.scatter(coords[1:, 0], coords[1:, 1], c='blue', label='Kupci')
    ax.scatter(coords[0, 0], coords[0, 1], c='red', marker='s', s=100, label='Depo')
    for i, (x, y) in enumerate(coords):
        ax.text(x + 1, y + 1, str(i), fontsize=8)
    ax.set_title(title)
    ax.legend()

print("Coordinates of depot and customers:")
print(coords)
# Prikaz slika
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
plot_routes(nn_routes, coords, "Nearest Neighbor (Total Distance:" +  str(round(nn_distance,2)) +")", ax1)
plot_routes(exact_routes, coords, "Exact algorithm (Total Distance:" + str(round(exact_distance,2)) + ")", ax2)
#plot_routes(ant_routes, coords, "Ant Colony (Total Distance:" + str(round(ant_distance,2)) + ")", ax3)
plt.tight_layout()
plt.show()
