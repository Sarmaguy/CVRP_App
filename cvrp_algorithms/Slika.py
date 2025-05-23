import numpy as np
import matplotlib.pyplot as plt

# Fiksirane koordinate (isti seed za konzistentnost)
np.random.seed(42)
depot = np.array([50, 50])
customers = np.random.uniform(0, 100, size=(15, 2))
coords = np.vstack([depot, customers])  # Prva točka je depo (index 0)

# Definicije ruta
nn_routes = [[9, 10, 11], [5, 6, 7, 8, 14, 15], [2, 3], [12, 13, 4], [1]]
cw_routes = [[1], [2, 7], [8, 11], [9, 10, 14, 6], [13, 3, 5, 12, 4], [15]]

# Funkcija za crtanje ruta
def plot_routes(routes, coords, title, ax, color):
    for route in routes:
        path = [0] + route + [0]  # početak i kraj u depou
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

# Prikaz slika
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
plot_routes(nn_routes, coords, "Nearest Neighbor (Total Distance: 773)", ax1, 'green')
plot_routes(cw_routes, coords, "Clarke-Wright (Total Distance: 707)", ax2, 'orange')
plt.tight_layout()
plt.show()
