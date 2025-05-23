import pulp
import numpy as np


def nearest_neighbor(distance_matrix, demands, capacity):
    n = len(demands)  # broj kupaca (bez depoa)
    visited = [False] * n
    routes = []

    while not all(visited):
        route = []
        load = 0
        current = 0  # krećemo iz depoa (indeks 0)

        while True:
            next_customer = None
            min_distance = float('inf')

            for i in range(n):
                if not visited[i] and load + demands[i] <= capacity:
                    dist = distance_matrix[current][i + 1]  # +1 jer kupci kreću od indexa 1
                    if dist < min_distance:
                        min_distance = dist
                        next_customer = i+1

            if next_customer is None:
                break  # nema više dostupnih kupaca za ovu rutu

            route.append(next_customer)
            visited[next_customer-1] = True
            load += demands[next_customer-1]
            current = next_customer + 1  # sljedeći "trenutni" je taj kupac

        routes.append(route)

    return routes

def clarke_wright(distance_matrix, demands, capacity):
    print(distance_matrix, demands, capacity)
    n = len(demands)
    routes = [[i+1] for i in range(n)]  # inicijalno: svaki kupac ima svoju rutu
    route_loads = [demands[i] for i in range(n)]

    # Izračun ušteda: S_ij = c_0i + c_0j - c_ij
    savings = []
    for i in range(n):
        for j in range(i + 1, n):
            s = distance_matrix[0][i + 1] + distance_matrix[0][j + 1] - distance_matrix[i + 1][j + 1]
            savings.append((s, i, j))

    # Sortiraj uštede silazno
    savings.sort(reverse=True)

    # Spoji rute na temelju najvećih ušteda
    for s, i, j in savings:
        route_i = None
        route_j = None

        for r in routes:
            if r[0] == i or r[-1] == i:
                route_i = r
            if r[0] == j or r[-1] == j:
                route_j = r

        # Ako su već u istoj ruti ili ne postoje – preskoči
        if route_i is None or route_j is None or route_i == route_j:
            continue

        total_demand = sum(demands[k] for k in route_i + route_j)
        if total_demand > capacity:
            continue  # ne može se spojiti – prelazi kapacitet

        # Provjeri jesu li krajevi kompatibilni za spajanje
        if route_i[-1] == i and route_j[0] == j:
            route_i.extend(route_j)
            routes.remove(route_j)
        elif route_j[-1] == j and route_i[0] == i:
            route_j.extend(route_i)
            routes.remove(route_i)

    return routes

def solve_cvrp_branch_and_cut(distance_matrix, demands, capacity):
    n = len(distance_matrix)
    customers = list(range(1, n))  # depot is node 0
    nodes = list(range(n))

    # Create the problem
    prob = pulp.LpProblem("CVRP", pulp.LpMinimize)

    # Decision variables: x[i][j] = 1 if route goes from i to j
    x = pulp.LpVariable.dicts("x", ((i, j) for i in nodes for j in nodes if i != j), cat='Binary')

    # Auxiliary variables for subtour elimination (MTZ formulation)
    u = pulp.LpVariable.dicts("u", customers, lowBound=0, upBound=capacity, cat='Continuous')

    # Objective: Minimize total distance
    prob += pulp.lpSum(distance_matrix[i][j] * x[i, j] for i in nodes for j in nodes if i != j)

    # Constraints:

    # 1. Each customer is entered exactly once
    for j in customers:
        prob += pulp.lpSum(x[i, j] for i in nodes if i != j) == 1

    # 2. Each customer is exited exactly once
    for i in customers:
        prob += pulp.lpSum(x[i, j] for j in nodes if i != j) == 1

    # 3. Vehicle must leave and return to depot
    prob += pulp.lpSum(x[0, j] for j in customers) <= len(customers)
    prob += pulp.lpSum(x[i, 0] for i in customers) <= len(customers)

    # 4. Subtour elimination constraints (MTZ)
    for i in customers:
        for j in customers:
            if i != j:
                prob += u[i] - u[j] + capacity * x[i, j] <= capacity - demands[j - 1]  # shifted index

    # 5. Load consistency
    for i in customers:
        prob += u[i] >= demands[i - 1]  # shifted index
        prob += u[i] <= capacity

    # Solve
    solver = pulp.PULP_CBC_CMD(msg=True)
    prob.solve(solver)

    # Extract solution
    routes = []
    if pulp.LpStatus[prob.status] == 'Optimal':
        route = [0]
        visited = set()
        current = 0
        while len(visited) < len(customers):
            for j in nodes:
                if current != j and (current, j) in x and pulp.value(x[current, j]) > 0.5:
                    route.append(j)
                    if j != 0:
                        visited.add(j)
                    current = j
                    if current == 0:
                        routes.append(route)
                        route = [0]
                        current = 0
                    break
        if route != [0]:
            routes.append(route)

    return routes, pulp.value(prob.objective)

def calculate_total_distance(routes, distance_matrix):
    total_distance = 0
    for route in routes:
        for i in range(len(route) - 1):
            total_distance += distance_matrix[route[i]][route[i + 1]]
        total_distance += distance_matrix[route[-1]][0]  # povratak u depo
    return total_distance

# distance_matrix = [
#     [0, 47, 25, 49, 57, 23, 67, 44, 45, 20, 22, 38, 25, 29, 30, 46],
#     [47, 0, 50, 82, 33, 33, 35, 87, 79, 43, 66, 85, 59, 18, 47, 93],
#     [25, 50, 0, 73, 73, 17, 80, 40, 69, 43, 43, 47, 50, 33, 54, 57],
#     [49, 82, 73, 0, 72, 71, 83, 68, 4, 40, 31, 46, 25, 70, 36, 45],
#     [57, 33, 73, 72, 0, 57, 11, 101, 69, 42, 69, 91, 55, 41, 38, 98],
#     [23, 33, 17, 71, 57, 0, 64, 55, 67, 35, 45, 57, 46, 16, 45, 66],
#     [67, 35, 80, 83, 11, 64, 0, 111, 80, 53, 79, 102, 66, 47, 49, 109],
#     [44, 87, 40, 68, 101, 55, 111, 0, 65, 61, 41, 23, 56, 69, 70, 29],
#     [45, 79, 69, 4, 69, 67, 80, 65, 0, 36, 27, 43, 21, 66, 33, 43],
#     [20, 43, 43, 40, 42, 35, 53, 61, 36, 0, 27, 49, 16, 30, 11, 56],
#     [22, 66, 43, 31, 69, 45, 79, 41, 27, 27, 0, 24, 16, 49, 32, 29],
#     [38, 85, 47, 46, 91, 57, 102, 23, 43, 49, 24, 0, 39, 66, 56, 10],
#     [25, 59, 50, 25, 55, 46, 66, 56, 21, 16, 16, 39, 0, 45, 17, 44],
#     [29, 18, 33, 70, 41, 16, 47, 69, 66, 30, 49, 66, 45, 0, 37, 75],
#     [30, 47, 54, 36, 38, 45, 49, 70, 33, 11, 32, 56, 17, 37, 0, 61],
#     [46, 93, 57, 45, 98, 66, 109, 29, 43, 56, 29, 10, 44, 75, 61, 0]
# ]

# demands = [ 6, 9, 10, 6, 1, 1, 2, 8, 7, 10, 3, 5, 6, 3, 5]
#   # svi kupci traže po 10
# capacity = 20  # stane do 3 kupca

# routes1 = nearest_neighbor(distance_matrix, demands, capacity)
# routes2 = clarke_wright(distance_matrix, demands, capacity)
# print("Nearest Neighbor Routes:")
# print(routes1)
# print("Total Distance:", calculate_total_distance(routes1, distance_matrix))
# print("Clarke-Wright Routes:")
# print(routes2)
# print("Total Distance:", calculate_total_distance(routes2, distance_matrix))

