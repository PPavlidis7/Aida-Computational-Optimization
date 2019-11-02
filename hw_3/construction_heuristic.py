from hw_3 import vrp_parser
import random


def calculate_manhattan_distance(from_node, to_note, node_coords):
    return (abs(node_coords[from_node]['x'] - node_coords[to_note]['x']) +
            abs(node_coords[from_node]['y'] - node_coords[to_note]['y']))


def find_next_node(current_node, node_coords, demands, truck):
    best_val = None
    next_node = None
    next_node_distance = None
    for node_id, demand in demands.items():

        if demand and truck['remained_capacity'] > demand and \
                (best_val is None
                 or best_val < demand / calculate_manhattan_distance(current_node, node_id, node_coords)):

            manhattan_distance = calculate_manhattan_distance(current_node, node_id, node_coords)
            best_val = demand / manhattan_distance
            next_node_distance = manhattan_distance
            next_node = node_id

    return next_node, next_node_distance


def calculate_path_truck(first_node_to_visit, node_coords, demands, depot, truck):
    current_node = depot
    if demands[first_node_to_visit] != 0:
        truck['notes_visited'].append(first_node_to_visit)
        truck['remained_capacity'] -= demands[first_node_to_visit]
        truck['demand_covered'] += demands[first_node_to_visit]
        truck['distance_made'] += calculate_manhattan_distance(current_node, first_node_to_visit, node_coords)
        demands[first_node_to_visit] = 0
        current_node = first_node_to_visit

    while truck['remained_capacity']:
        current_node, distance_made = find_next_node(current_node, node_coords, demands, truck)
        if current_node is None:
            current_node = truck['notes_visited'][len(truck['notes_visited']) - 1]
            break
        truck['notes_visited'].append(current_node)
        truck['remained_capacity'] -= demands[current_node]
        truck['demand_covered'] += demands[current_node]
        truck['distance_made'] += distance_made
        demands[current_node] = 0

    # return to depot
    truck['notes_visited'].append(depot)
    truck['distance_made'] += calculate_manhattan_distance(current_node, depot, node_coords)


def generate_construction_heuristic(header, node_coords, demands, depot):
    number_of_trucks = header['num_of_trucks']
    trucks = {}
    first_steps = random.sample(list(node_coords), number_of_trucks)
    for truck_id in range(number_of_trucks):
        trucks[truck_id] = {
            'remained_capacity': header['truck_capacity'],
            'notes_visited': [depot],
            'demand_covered': 0,
            'distance_made': 0
        }
        calculate_path_truck(first_steps[truck_id], node_coords, demands, depot, trucks[truck_id])
    print_results(trucks, demands)


def print_results(trucks, demands):
    for trucks in trucks:
        pass



def main():
    header, node_coords, demands, depot = vrp_parser.main()
    construction_heuristic = generate_construction_heuristic(header, node_coords, demands, depot)


if __name__ == '__main__':
    main()
