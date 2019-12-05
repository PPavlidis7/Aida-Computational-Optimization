import time
from random import shuffle

import construction_heuristic as con_heu


def reorder_truck_path(truck, node_coords):
    """ truck path's first node will be kept. The other nodes will be shuffled"""
    best_distance = truck['distance_made']
    # if we find 4 continuous worse paths we exit from new_path_calculation
    counter_worse__continuous_path = 0
    # each truck will have 1 minutes to find a better path
    start_time = time.time()
    while time.time() - start_time < 60 and counter_worse__continuous_path < 4:
        temp_copy = truck['notes_visited'][2:]
        shuffle(temp_copy)
        potentially_new_path = [truck['notes_visited'][0]] + temp_copy
        new_distance = 0
        for index in range(len(potentially_new_path) - 1):
            new_distance += con_heu.calculate_manhattan_distance(potentially_new_path[index],
                                                                 potentially_new_path[index + 1], node_coords)

        if new_distance < best_distance:
            counter_worse__continuous_path = 0
            best_distance = new_distance
            truck['notes_visited'][2:] = temp_copy
        else:
            counter_worse__continuous_path += 1
    truck['distance_made'] = best_distance


def improvement_heuristic(node_coords, trucks, value_to_improve):
    previous_best_cost = value_to_improve
    """ We give 600 secs to this program to improve our first solution. At first, we shuffle a part of trucks' paths.
    If this shuffling does not improve our solution, then we shuffle the whole path for each truck and then start again
    the previous calculation (path's part shuffling.
    """
    new_total_distance_made = 0
    start_time = time.time()
    while time.time() - start_time < 600:
        for truck_id, truck in trucks.items():
            reorder_truck_path(truck, node_coords)
            new_total_distance_made += truck['distance_made']

        if new_total_distance_made < previous_best_cost:
            previous_best_cost = new_total_distance_made


def main():
    # file_name = '../hw_1/A/A-n38-k5.vrp'
    file_name = input("Give file's name\n")
    header, node_coords, demands, depot, trucks, value_to_improve = con_heu.main(file_name)
    if header and node_coords and demands and depot and trucks and value_to_improve:
        improvement_heuristic(node_coords, trucks, value_to_improve)
        print('----IMPROVEMENT HEURISTIC SOLUTION----')
        con_heu.print_results(trucks)


if __name__ == '__main__':
    main()
