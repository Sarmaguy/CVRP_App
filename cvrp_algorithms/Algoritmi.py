import pulp
import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


def nearest_neighbor(distance_matrix, demands, capacity):
    print("distance_matrix:", distance_matrix)
    print("demands:", demands)
    print("capacity:", capacity)
    n_customers = len(demands)
    unvisited = set(range(1, n_customers + 1))  # Customers are 1 to n
    routes = []

    while unvisited:
        route = [0]  # Start from depot
        load = 0
        current = 0

        while True:
            next_customer = None
            min_distance = float('inf')

            for customer in unvisited:
                if load + demands[customer - 1] <= capacity:
                    dist = distance_matrix[current][customer]
                    if dist < min_distance:
                        min_distance = dist
                        next_customer = customer

            if next_customer is None:
                break  # No feasible customer can be added, return to depot

            route.append(next_customer)
            load += demands[next_customer - 1]
            unvisited.remove(next_customer)
            current = next_customer

        route.append(0)  # Return to depot
        routes.append(route)

    return routes, calculate_total_distance(routes, distance_matrix)

def clarke_wright(distance_matrix, demands, capacity):
    from collections import deque

    n = len(demands)  # number of customers
    total_nodes = n + 1  # including depot at index 0

    # Initial routes: each customer served by one vehicle
    routes = {i + 1: deque([0, i + 1, 0]) for i in range(n)}
    route_loads = {i + 1: demands[i] for i in range(n)}

    # Compute savings
    savings = []
    for i in range(1, total_nodes):
        for j in range(i + 1, total_nodes):
            if i == j: continue
            save = distance_matrix[i][0] + distance_matrix[0][j] - distance_matrix[i][j]
            savings.append((save, i, j))
    savings.sort(reverse=True)

    # Merge routes based on savings
    for save, i, j in savings:
        # Find routes that contain i and j
        ri = rj = None
        for key, route in routes.items():
            if route[1] == i:
                ri = key
            if route[-2] == j:
                rj = key

        if ri is None or rj is None or ri == rj:
            continue

        # Check if i is at the end of its route and j at the start of its route
        if routes[ri][-2] == i and routes[rj][1] == j:
            load = route_loads[ri] + route_loads[rj]
            if load <= capacity:
                # Merge rj into ri
                routes[ri].pop()  # remove depot at end
                routes[rj].popleft()  # remove depot at start
                routes[ri].extend(routes[rj])
                route_loads[ri] = load
                del routes[rj]

    # Return routes as list of lists
    return [list(route) for route in routes.values()], calculate_total_distance(routes.values(), distance_matrix)

def google(distance_matrix, demands, vehicle_capacity):
    # OR-Tools expects demand for every node, so prepend depot demand (0)
    demands = [0] + demands
    num_locations = len(distance_matrix)
    num_vehicles = (sum(demands) + vehicle_capacity - 1) // vehicle_capacity
    depot = 0

    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_index)

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]

    demand_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_index,
        0,
        [vehicle_capacity] * num_vehicles,
        True,
        'Capacity'
    )

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    solution = routing.SolveWithParameters(search_params)

    routes = []
    if solution:
        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)
                index = solution.Value(routing.NextVar(index))
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            if len(route) > 2:  # Only include non-empty routes (depot → something → depot)
                routes.append(route)
    return routes, calculate_total_distance(routes, distance_matrix)

def calculate_total_distance(routes, distance_matrix):
    total_distance = 0
    for route in routes:
        for i in range(len(route) - 1):
            total_distance += distance_matrix[route[i]][route[i + 1]]
        total_distance += distance_matrix[route[-1]][0]  # povratak u depo
    return total_distance


def ant_colony(distance_matrix, demands, capacity, n_ants=10, n_iterations=100, alpha=1.0, beta=5.0, evaporation_rate=0.5, Q=100):
    import random
    n_customers = len(demands)
    n_nodes = n_customers + 1  # including depot at index 0

    pheromone = [[1.0 for _ in range(n_nodes)] for _ in range(n_nodes)]
    best_routes = []
    best_distance = float('inf')

    def choose_next_node(current, unvisited, load):
        probabilities = []
        for node in unvisited:
            if load + demands[node - 1] > capacity:
                probabilities.append(0)
                continue
            tau = pheromone[current][node] ** alpha
            eta = (1.0 / distance_matrix[current][node]) ** beta
            probabilities.append(tau * eta)
        total = sum(probabilities)
        if total == 0:
            return None
        probabilities = [p / total for p in probabilities]
        return random.choices(list(unvisited), weights=probabilities)[0]

    def construct_solution():
        solution = []
        unvisited = set(range(1, n_nodes))
        while unvisited:
            route = [0]
            load = 0
            current = 0
            while True:
                next_node = choose_next_node(current, unvisited, load)
                if next_node is None:
                    break
                route.append(next_node)
                load += demands[next_node - 1]
                unvisited.remove(next_node)
                current = next_node
            route.append(0)
            solution.append(route)
        return solution

    for _ in range(n_iterations):
        all_solutions = []
        for _ in range(n_ants):
            routes = construct_solution()
            total_dist = calculate_total_distance(routes, distance_matrix)
            all_solutions.append((routes, total_dist))
            if total_dist < best_distance:
                best_distance = total_dist
                best_routes = routes

        # Evaporation
        for i in range(n_nodes):
            for j in range(n_nodes):
                pheromone[i][j] *= (1 - evaporation_rate)

        # Deposit
        for routes, dist in all_solutions:
            for route in routes:
                for i in range(len(route) - 1):
                    a, b = route[i], route[i + 1]
                    pheromone[a][b] += Q / dist
                    pheromone[b][a] += Q / dist  # Assuming symmetric distances

    return best_routes, best_distance

def exact(distance_matrix, demands, capacity, time_limit=None, msg=False):
    n = len(demands)
    N = n + 1 # nodes including depot


    # Indices
    nodes = range(N)
    customers = range(1, N)


    # Helpers
    def arc_list():
        return [(i, j) for i in nodes for j in nodes if i != j]


    arcs = arc_list()


    # Model
    prob = pulp.LpProblem("CVRP_exact_SCF", pulp.LpMinimize)


    # Decision vars
    x = pulp.LpVariable.dicts('x', (nodes, nodes), lowBound=0, upBound=1, cat=pulp.LpBinary)
    y = pulp.LpVariable.dicts('y', (nodes, nodes), lowBound=0, cat=pulp.LpContinuous) # flow on arc (i,j)


    # Objective
    prob += pulp.lpSum(distance_matrix[i][j] * x[i][j] for (i, j) in arcs)


    # No self loops
    for i in nodes:
        prob += x[i][i] == 0
        prob += y[i][i] == 0

    
    for i in customers:
        prob += pulp.lpSum(x[i][j] for j in nodes if j != i) == 1
        prob += pulp.lpSum(x[j][i] for j in nodes if j != i) == 1


    # Depot flow (can have multiple vehicles): balance in = out
    prob += pulp.lpSum(x[0][j] for j in customers) == pulp.lpSum(x[j][0] for j in customers)


    # Single-commodity flow conservation
    total_demand = sum(demands)
    # Depot ships total demand
    prob += pulp.lpSum(y[0][j] for j in customers) - pulp.lpSum(y[j][0] for j in customers) == total_demand


    for i in customers:
    # Inflow - outflow equals demand(i)
        prob += pulp.lpSum(y[j][i] for j in nodes if j != i) - pulp.lpSum(y[i][j] for j in nodes if j != i) == demands[i - 1]


    # Capacity coupling: 0 <= y_ij <= Q * x_ij
    for (i, j) in arcs:
        prob += y[i][j] <= capacity * x[i][j]




    # Solve
    solver = pulp.PULP_CBC_CMD(msg=msg, timeLimit=time_limit) if time_limit else pulp.PULP_CBC_CMD(msg=msg)
    prob.solve(solver)


    # Extract routes
    # Build adjacency from chosen arcs
    adj = {i: [] for i in nodes}
    for (i, j) in arcs:
        if pulp.value(x[i][j]) > 0.5:
            adj[i].append(j)


    routes = []
    used = set()


    # Start a route from each arc leaving the depot
    for j in adj[0]:
        if j in used:
            continue
        route = [0, j]
        used.add(j)
        cur = j
        while True:
            nxts = [k for k in adj[cur] if k != cur] # should be exactly one
            if not nxts:
            # Should not happen in a feasible solution
                break
            nxt = nxts[0]
            route.append(nxt)
            if nxt == 0:
                break
            used.add(nxt)
            cur = nxt
        # Ensure route ends at depot
        if route[-1] != 0:
            route.append(0)
        routes.append(route)


    total_cost = calculate_total_distance(routes, distance_matrix)


    status = pulp.LpStatus[prob.status]
    prob_status = {"status": status, "objective": pulp.value(prob.objective)}



    return routes, total_cost


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

