"""
    This script is a generator for CVRP problems

    User can call the module with two ways:
    1: python3 cvrp_generator.py <dimension> <capacity> <file_name>
    2: python3 cvrp_generator.py

    If user selects the second way, we ask him to give these values
"""
import sys
import random
import time

random.seed(int(time.time()))


def generate_data(dimension, capacity, file_name):
    header_data = create_header(dimension, capacity, file_name)
    nodes_data = generate_nodes(dimension)
    nodes_demands = generate_demand_data(dimension)
    depot_section = str(random.randint(1, dimension))
    write_data_to_file(header_data, nodes_data, nodes_demands, depot_section, file_name)


def write_data_to_file(header, nodes, demands, depot, file_name):
    data_to_write = '\n'.join(header) + '\nNODE_COORD_SECTION\n'

    for node_id, coords in nodes.items():
        data_to_write += '{}\t{}\t{}\n'.format(node_id, coords[0], coords[1])
    data_to_write += 'DEMAND_SECTION\n'

    for node_id, demand in demands.items():
        data_to_write += '{}\t{}\n'.format(node_id, demand)
    data_to_write += 'DEPOT_SECTION\n' + '{}\n-1\nEOF'.format(depot)

    with open(file_name + '.vrp.', 'w') as f:
        f.write(data_to_write)


def generate_demand_data(dimension):
    demand_upper_bound = 10
    nodes_demands = {}
    for node_id in range(1, dimension + 1):
        nodes_demands[node_id] = random.randint(1, demand_upper_bound)
    return nodes_demands


def generate_nodes(dimension):
    nodes = {}
    seen_nodes = set()
    coords_upper_bound = 2000

    while coords_upper_bound**2 < dimension:
        coords_upper_bound += dimension

    for node_id in range(1, dimension + 1):
        x, y = random.randint(0, coords_upper_bound), random.randint(0, coords_upper_bound)
        while (x, y) in seen_nodes:     # create unique coords pairs
            x, y = random.randint(0, dimension), random.randint(0, dimension)
        seen_nodes.add((x, y))
        nodes[node_id] = x, y

    return nodes


def create_header(dimension, capacity, file_name):
    header_data = ['NAME: ' + file_name, 'TYPE: CVRP', 'DIMENSION: %d' % dimension, 'CAPACITY: %d' % capacity]
    return header_data


def main():
    arg_names = ['command', 'dimension', 'capacity', 'file_name']
    users_args = dict(zip(arg_names, sys.argv))

    if 'dimension' not in users_args:
        while True:
            user_input = input("Give dimension\n")
            try:
                users_args['dimension'] = int(user_input)
                break
            except ValueError:
                pass

    if 'capacity' not in users_args:
        while True:
            user_input = input("Give capacity\n")
            try:
                users_args['capacity'] = int(user_input)
                break
            except ValueError:
                pass

    if 'file_name' not in users_args:
        users_args['file_name'] = 'cvrp_{}_{}'.format(users_args['dimension'], users_args['capacity'])

    generate_data(int(users_args['dimension']), int(users_args['capacity']), users_args['file_name'])


if __name__ == '__main__':
    main()
