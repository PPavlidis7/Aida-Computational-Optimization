"""
    This is a parser for mps files. Its returns A, b, c, Eqin, c0, MinMax
"""
import re
import warnings

import numpy as np
import pandas

warnings.filterwarnings("ignore")


def __read_file(file_name):
    """
    :param file_name: string
    :return: tuple

    Read file and return its data as tuple
    """
    with open(file_name, 'r') as f:
        return tuple(f.readlines())


def __find_c0(line):
    """
    :param line: string
    :return: string

    Find c0 in line if exists and return its value. Otherwise return 0.
    """
    re_find_c0_number = re.compile("(?:=).* [-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d{2} ) ?",
                                   re.VERBOSE)
    c0 = re_find_c0_number.findall(line)
    if len(c0):
        c0 = float(re.sub("=", "", c0[0]))
    else:
        c0 = 0.0
    return c0


def __handle_file_data(file_data):
    """
    :param file_data: list
    :return: tuple

    Return a_matrix_values, b_vector, c_vector, eqin, c0_value, min_max
    """
    line_index = 0
    min_max = None
    row_names = []
    objective__func_name = ''
    eqin = []

    try:
        # NAME section
        if 'NAME' in file_data[0]:
            problem_name = file_data[line_index][14:22].strip()
            if 'maximization' in file_data[line_index]:
                min_max = 1
            else:
                min_max = -1
            line_index += 1
            if 'ROWS' not in file_data[line_index]:
                raise SyntaxError("Wrong file format. Expected ROWS section after NAME section")
            c0_value = __find_c0(file_data[0])
            line_index += 1
        else:
            raise SyntaxError("Wrong file format. Expected problem's name at first line")

        # ROWS section
        line = file_data[line_index]
        while line[:7] != 'COLUMNS':
            if not line:
                raise SyntaxError("file has no 'COLUMNS' section")

            # skip empty lines and comments
            if len(line.strip()) == 0 or line[0] == '*' or line[0] == '$':
                pass
            else:
                _constraint_type = line[1:3].strip()
                _constraint_name = line[4:12].strip()
                if _constraint_type == 'N':
                    objective__func_name = _constraint_name
                elif _constraint_type == 'G':
                    eqin.append(1)
                elif _constraint_type == 'L':
                    eqin.append(-1)
                elif _constraint_type == 'E':
                    eqin.append(0)
                row_names.append(_constraint_name)

            line_index += 1
            line = file_data[line_index]
        line_index += 1

        # COLUMNS section
        a_matrix = pandas.DataFrame({'contraint_names': row_names}, index=row_names)
        a_matrix.drop(columns='contraint_names', inplace=True)

        # "in" operator is faster at sets than lists. Average: O(1) for sets and O(n) for lists
        # source: https://wiki.python.org/moin/TimeComplexity
        row_names_set = set(row_names)

        line = file_data[line_index]
        while line[:3] != 'RHS':
            if not line:
                raise SyntaxError("EOF reached before 'RHS' section was found")
                # skip empty lines and comments
            if len(line.strip()) == 0 or line[0] == '*' or line[0] == '$':
                pass
            else:
                _variable_name = line[4:12].strip()
                if _variable_name not in a_matrix.columns.values:
                    a_matrix[_variable_name] = 0.0
                _var_belong_to_constraint = line[14:22].strip()
                if _var_belong_to_constraint not in row_names_set:
                    raise KeyError("no constraint name '%s'" % _var_belong_to_constraint)
                _variable_value = float(line[24:36])
                a_matrix.at[_var_belong_to_constraint, _variable_name] = _variable_value

                _next_constraint = line[39:47].strip()
                if _next_constraint:
                    if _next_constraint not in row_names_set:
                        raise KeyError("no constraint name '%s'" % _next_constraint)
                    _variable_value = float(line[49:61])
                    a_matrix.at[_next_constraint, _variable_name] = _variable_value
            line_index += 1
            line = file_data[line_index]
        line_index += 1

        # RHS SECTION
        # add b column at dataFrame
        a_matrix['b'] = 0.0
        line = file_data[line_index]
        while line[:6] != 'RANGES' and line[:6] != 'BOUNDS' and line[:6] != 'ENDATA':
            if not line:
                raise SyntaxError("EOF reached before 'ENDATA' was found")
            if len(line.strip()) == 0 or line[0] == '*':
                pass
            else:
                _constraint_name = line[14:22].strip()
                if _constraint_name not in row_names_set:
                    raise KeyError("no constraint name '%s'" % _constraint_name)

                _b_value = float(line[24:36].strip())
                a_matrix.at[_constraint_name, 'b'] = _b_value

                _next_constraint_name = line[39:47].strip()
                if _next_constraint_name:
                    if _next_constraint_name not in row_names_set:
                        raise KeyError("no constraint name '%s'" % _next_constraint_name)
                    _b_value = float(line[24:36].strip())
                    a_matrix.at[_next_constraint_name, 'b'] = _b_value
            line_index += 1
            line = file_data[line_index]
        line_index += 1

        # reach ENDATA
        while line[:6] != 'ENDATA':
            if not line:
                raise SyntaxError("EOF reached before 'ENDATA' was found")
            line_index += 1
            line = file_data[line_index]

        if 'ENDATA' not in line:
            raise SyntaxError("EOF reached before 'ENDATA' was found")

        a_matrix_values, b_vector, c_vector = __process_values(a_matrix, objective__func_name)
        # convert lists and vectors to numpy types in order to improve performance
        # (less memory usage and faster modifications)
        return np.asarray(a_matrix_values), np.asarray(b_vector), np.asarray(c_vector), np.asarray(eqin), c0_value, \
            min_max
    except IndexError:
        raise SyntaxError('Wrong file format. Find ENDATA before read all the needed data')


def __process_values(df, objective__func_name):
    """
    :param df: pandas.dataFrame
    :param objective__func_name: string
    :return: tuple

    Transform a_matrix_values, b_vector and c_vector in the appropriate format
    """
    # A matrix
    a_matrix_values = df.drop('b', axis=1)

    # c vector
    c_vector = a_matrix_values[a_matrix_values.index.str.startswith(objective__func_name)].values.tolist()[0]

    a_matrix_values = a_matrix_values.values.tolist()

    # b vector
    b_vector = df['b'].values.tolist()

    return a_matrix_values, b_vector, c_vector


def parse_file(file_name):
    """
    :param file_name: string
    :return: tuple

    Read file's data and return A, b, c, Eqin, c0, MinMax
    """
    # read file
    file_data = __read_file(file_name)
    # parse data
    return __handle_file_data(file_data)
