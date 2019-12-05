import operator
import random

import vrp_parser


def calculate_manhattan_distance(from_node, to_note, node_coords):
    return (abs(node_coords[from_node]['x'] - node_coords[to_note]['x']) +
            abs(node_coords[from_node]['y'] - node_coords[to_note]['y']))


def update_acceptable_nodes(best_values, node_id, new_value):
    best_values_sorted = sorted(best_values, key=operator.itemgetter(1))
    if GRASP_LIST_SIZE > len(best_values_sorted):
        best_values_sorted.append([node_id, new_value])
        return best_values_sorted
    else:
        if best_values_sorted[len(best_values_sorted) - 1][0] > new_value:
            best_values_sorted[len(best_values_sorted) - 1] = [node_id, new_value]
        return best_values_sorted


def find_next_node(current_node, node_coords, demands, truck):
    best_val = []
    for node_id, demand in demands.items():
        if node_id != current_node and demand and truck['remained_capacity'] > demand:
            manhattan_distance = calculate_manhattan_distance(current_node, node_id, node_coords)
            cost_value = demand / manhattan_distance
            best_val = update_acceptable_nodes(best_val, node_id, cost_value)

    if len(best_val) > 0:
        selected_next_node = random.choice(best_val)
        return selected_next_node[0], selected_next_node[1]
    else:
        return None, None


def calculate_path_truck(first_node_to_visit, node_coords, demands, depot, truck):
    current_node = depot
    # some calculations for the first node that each track will visit
    if demands[first_node_to_visit] != 0:
        truck['notes_visited'].append(first_node_to_visit)
        truck['remained_capacity'] -= demands[first_node_to_visit]
        truck['demand_covered'] += demands[first_node_to_visit]
        truck['distance_made'] += calculate_manhattan_distance(current_node, first_node_to_visit, node_coords)
        demands[first_node_to_visit] = 0
        current_node = first_node_to_visit

    # the rest nodes that each track will visit
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
    global GRASP_LIST_SIZE
    GRASP_LIST_SIZE = 8
    if len(node_coords) < 8:
        if len(node_coords) < number_of_trucks:
            raise IOError("There is an error with datas")
        GRASP_LIST_SIZE = len(node_coords)

    trucks = {}
    # calculate the distance from depot for all nodes
    distances = []
    for node_id, node in node_coords.items():
        if node_id == depot:
            continue
        distances.append([node_id, calculate_manhattan_distance(depot, node_id, node_coords)])
    distances.sort(key=operator.itemgetter(1))

    # select first 5 nodes as first step for each truck
    first_steps_acceptable = [distances[index][0] for index in range(GRASP_LIST_SIZE)]
    first_steps = random.sample(first_steps_acceptable, number_of_trucks)
    while not all(remained_demand == 0 for node_id, remained_demand in demands.items()):
        for truck_id in range(number_of_trucks):
            trucks[truck_id] = {
                'remained_capacity': header['truck_capacity'],
                'notes_visited': [depot],
                'demand_covered': 0,
                'distance_made': 0
            }
            calculate_path_truck(first_steps[truck_id], node_coords, demands, depot, trucks[truck_id])

    return trucks


def print_results(trucks):
    total_demand = 0
    total_distance_made = 0
    for truck_id, truck in trucks.items():
        total_demand += truck['demand_covered']
        total_distance_made += truck['distance_made']
        print("Truck {} path: {}".format(str(truck_id), ' '.join(map(str, truck['notes_visited']))))

    print("Total distance made: ", total_distance_made)
    print('The amount of demand that we covered: ', total_demand)
    return total_distance_made


def check_file(node_coords):
    """
        This function checks if there are two nodes in the same coords. If yes, we can't use this file since
        manhattan distance for this nodes is zero and this will raise an ZeroDivisionError at find_next_node function
    """
    unique_nodes = set([(coords['x'], coords['y']) for node_id, coords in node_coords.items()])
    return len(unique_nodes) == len(node_coords)


def main():
    # file_name = '../hw_1/A/A-n38-k5.vrp'
    file_name = input("Give file's name\n")
    header, node_coords, demands, depot = vrp_parser.main(file_name)
    # check if file is ok
    file_is_ok = check_file(node_coords)
    if file_is_ok:
        trucks = generate_construction_heuristic(header, node_coords, demands, depot)

        # print construction heuristic solution
        print('----CONSTRUCTION HEURISTIC SOLUTION----')
        print_results(trucks)
    else:
        print("File {} had problem so I skipped it".format(file_name))


if __name__ == '__main__':
    main()
