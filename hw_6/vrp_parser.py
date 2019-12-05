"""
    This script is a parser for problems from CVRPLIB (Capacitated Vehicle Routing Problem Library)
    http://vrp.galgos.inf.puc-rio.br/index.php/en

    Some vrp files from other libraries might have TIME_WINDOW_SECTION, STAND_TIME_SECTION 
    and PICKUP_SECTION. For those files you must add more while-loops in read_file function. 
"""
import re


def read_file(file_name):
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

    if len(header) and len(node_coord) and len(demands) and len(depot):
        return (
            handle_header(header),
            handle_coords(node_coord),
            handle_demand(demands),
            float(depot[0][0])
        )
    else:
        print("Something went wrong with file parsing.")


def handle_header(header):
    header_data = {}
    for header_line in header:
        if header_line[0] == 'COMMENT':
            # a silly way to find easily the number of trucks
            for index, value in enumerate(header_line):
                if value == 'trucks:':
                    header_data['num_of_trucks'] = int(re.findall(r'\d+', header_line[index + 1].split(',')[0])[0])
        if header_line[0] == 'CAPACITY':
            header_data['truck_capacity'] = int(header_line[2])
            break
    return header_data


def handle_coords(coords):
    # <id> <x-coord> <y-coord> 
    coords_data = {}
    for coord_item in coords:
        coords_data[float(coord_item[0])] = {'x': float(coord_item[1]), 'y': float(coord_item[2])}
    return coords_data


def handle_demand(demands):
    # demand section data can be either <id> <dem> or <id> <weight> <vol>
    demands_data = {}
    for demand in demands:
        demands_data[float(demand[0])] = float(demand[1])
    return demands_data


def main(file_name):
    return read_file(file_name)
