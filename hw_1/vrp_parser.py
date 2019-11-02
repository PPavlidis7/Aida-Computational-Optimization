"""
    This script is a parser for problems from CVRPLIB (Capacitated Vehicle Routing Problem Library)
    http://vrp.galgos.inf.puc-rio.br/index.php/en

    Some vrp files from other libraries might have TIME_WINDOW_SECTION, STAND_TIME_SECTION 
    and PICKUP_SECTION. For those files you must add more while-loops in read_file function. 
"""
import sys


def read_file(file_name, print_to_console):
    header = []
    node_coord = []
    node_coord_section_found = False
    demands = []
    demands_section_found = False
    depot = []
    depot_section_found = False
    try:
        with open(file_name, 'r') as f:
            file_data = f.read()
    except FileNotFoundError:
        raise FileNotFoundError("File %s not found" % file_name)

    # check which of the supported sections are in our file
    if 'NODE_COORD_SECTION' in file_data: node_coord_section_found = True
    if 'DEMAND_SECTION' in file_data: demands_section_found = True
    if 'DEPOT_SECTION' in file_data: depot_section_found = True
    if 'EOF' not in file_data: raise EOFError('EOF not found')

    iterator = iter(file_data.split('\n'))
    while True:
        try:
            line = next(iterator)

            # read header
            while 'NODE_COORD_SECTION' not in line and 'DEMAND_SECTION' not in line and \
                    'DEPOT_SECTION' not in line and 'EOF' not in line:
                header.append(line.split())
                line = next(iterator)

            if node_coord_section_found and 'NODE_COORD_SECTION' in line:
                # read coords
                line = next(iterator)
                while 'DEMAND_SECTION' not in line and 'DEPOT_SECTION' not in line and 'EOF' not in line:
                    node_coord.append(line.split())
                    line = next(iterator)

            if demands_section_found and 'DEMAND_SECTION' in line:
                # read demands
                line = next(iterator)
                while 'NODE_COORD_SECTION' not in line and 'DEPOT_SECTION' not in line and 'EOF' not in line:
                    demands.append(line.split())
                    line = next(iterator)

            if depot_section_found and 'DEPOT_SECTION' in line:
                # read depot
                line = next(iterator)
                depot.append(line.split())  # <dep_id> or <x-coord> <y-coord>
                break

        except StopIteration:
            break

    if print_to_console == 'y':
        if len(header): handle_header(header)
        if len(node_coord): handle_coords(node_coord)
        if len(demands): handle_demand(demands)
        if len(depot): handle_depot(depot)
    else:
        write_to_file(header, node_coord, demands, depot)


def write_to_file(header, node_coord, demands, depot):
    data_to_write = ''
    if len(header):
        data_to_write += '----------HEADER DATA----------\n'
        for header_line in header:
            string_to_show = ' '.join(header_line)
            data_to_write += string_to_show + '\n'

    if len(node_coord):
        coords_data = {}
        for coord_item in node_coord:
            coords_data[float(coord_item[0])] = {'x': float(coord_item[1]), 'y': float(coord_item[2])}
        data_to_write += '----------COORDS DATA----------\n'
        data_to_write += 'node_id\tx\ty\n'
        sorted_node_ids = sorted(coords_data.keys())
        for node_id in sorted_node_ids:
            data_to_write += '{}\t{}\t{}\n'.format(node_id, coords_data[node_id]['x'], coords_data[node_id]['y'])

    if len(demands):
        demands_data = {}
        for demand in demands:
            demands_data[float(demand[0])] = float(demand[1])
        data_to_write += '----------DEMAND DATA----------\n'
        data_to_write += 'node_id\tdemand\n'
        sorted_node_ids = sorted(demands_data.keys())
        for node_id in sorted_node_ids:
            data_to_write += '{}\t{}\n'.format(node_id, demands_data[node_id])

    if len(depot):
        data_to_write += '----------DEPOT SECTION DATA----------\n'
        depot_to_write = ' '.join([value for depot_line in depot for value in depot_line])
        data_to_write += 'depot = ' + depot_to_write

    with open('parsing_result.txt.', 'w') as f:
        f.write(data_to_write)
    print("Data have been printed to file 'parsing_result.txt.'")


def handle_header(header):
    print('----------HEADER DATA----------')
    for header_line in header:
        string_to_show = ' '.join(header_line)
        print(string_to_show)


def handle_coords(coords):
    # <id> <x-coord> <y-coord> 
    coords_data = {}
    for coord_item in coords:
        coords_data[float(coord_item[0])] = {'x': float(coord_item[1]), 'y': float(coord_item[2])}
    print('----------COORDS DATA----------')
    print('node_id\tx\ty')
    sorted_node_ids = sorted(coords_data.keys())
    for node_id in sorted_node_ids:
        print('%d\t%d\t%d' % (node_id, coords_data[node_id]['x'], coords_data[node_id]['y']))


def handle_demand(demands):
    # demand section data can be either <id> <dem> or <id> <weight> <vol>
    demands_data = {}
    for demand in demands:
        demands_data[float(demand[0])] = float(demand[1])
    print('----------DEMAND DATA----------')
    print('node_id\tdemand')
    sorted_node_ids = sorted(demands_data.keys())
    for node_id in sorted_node_ids:
        print('%d\t%d' % (node_id, demands_data[node_id]))


def handle_depot(depot):
    print('----------DEPOT SECTION DATA----------')
    depot_to_show = ' '.join([value for depot_line in depot for value in depot_line])
    print('depot = ', depot_to_show)


def main():
    file_to_parse = sys.argv[1]
    # file_to_parse = 'Brussels1.vrp'
    print_to_console = input("Should I print the data in console? [y/n]\n")
    read_file(file_to_parse, print_to_console.lower())


if __name__ == "__main__":
    main()
