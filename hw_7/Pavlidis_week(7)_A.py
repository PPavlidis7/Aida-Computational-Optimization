"""
    This is a parser for mps files. Its results are written to the "output.txt" file
"""
import sys
import warnings

import numpy as np
import pandas

warnings.filterwarnings("ignore")


def __read_file(file_name):
    with open(file_name, 'r') as f:
        return tuple(f.readlines())


def handle_file_data(file_data):
    line_index = 0
    min_max = None
    row_names = []
    objective__func_name = ''
    eqin = []
    bs_array = []

    try:
        # NAME section
        if 'NAME' in file_data[0]:
            problem_name = file_data[line_index][14:22].strip()
            if 'maximization' in file_data[line_index]:
                min_max = '1'
            else:
                min_max = '-1'
            line_index += 1
            if 'ROWS' not in file_data[line_index]:
                raise SyntaxError("Wrong file format. Expected ROWS section after NAME section")
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
                    eqin.append('1')
                elif _constraint_type == 'L':
                    eqin.append('-1')
                elif _constraint_type == 'E':
                    eqin.append('0')
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

        # RANGES section
        if 'RANGES' in line:
            a_matrix['ranges'] = np.nan
            line = file_data[line_index]
            while line[:6] != 'BOUNDS' and line[:6] != 'ENDATA':
                if not line:
                    raise SyntaxError("EOF reached before 'ENDATA' was found")
                if len(line.strip()) == 0 or line[0] == '*':
                    pass
                else:
                    _constraint_name = line[14:22].strip()
                    if _constraint_name not in row_names_set:
                        raise KeyError("no constraint name '%s'" % _constraint_name)

                    _range_value = float(line[24:36].strip())
                    a_matrix.at[_constraint_name, 'ranges'] = _range_value

                    _next_constraint_name = line[39:47].strip()
                    if _next_constraint_name:
                        if _next_constraint_name not in row_names_set:
                            raise KeyError("no constraint name '%s'" % _next_constraint_name)
                        _range_value = float(line[24:36].strip())
                        a_matrix.at[_next_constraint_name, 'ranges'] = _range_value
                line_index += 1
                line = file_data[line_index]

        # BOUNDS  section
        if 'BOUNDS' in line:
            line_index += 1
            line = file_data[line_index]
            variable_names = set(a_matrix.columns.values)
            while line[:6] != 'ENDATA':
                if not line:
                    raise SyntaxError("EOF reached before 'ENDATA' was found")
                if len(line.strip()) == 0 or line[0] == '*':
                    pass
                else:
                    _variable_name = line[14:22].strip()
                    if _variable_name not in variable_names:
                        raise ValueError('unknown column label %s' % _variable_name)

                    _bound_type = line[1:3].strip()
                    if _bound_type == 'LO' or _bound_type == 'UP' or _bound_type == 'FX':
                        _bound_value = float(line[24:36].strip())
                        bs_array.append([_variable_name, _bound_type, _bound_value])
                    elif _bound_type == 'FR' or _bound_type == 'MI' or _bound_type == 'PL':
                        bs_array.append([_variable_name, _bound_type, 'None'])
                line_index += 1
                line = file_data[line_index]

        if 'ENDATA' not in line:
            raise SyntaxError("EOF reached before 'ENDATA' was found")

        print("File parsing finished. Wait until the results are written to the \"output.txt\" file")
        __write_values_to_file(a_matrix, eqin, bs_array, min_max, objective__func_name, row_names)
    except IndexError:
        raise SyntaxError('Wrong file format. Find ENDATA before read all the needed data')


def __write_values_to_file(df, eqin, bs_array, min_max, objective__func_name, row_names):
    output_file_name = 'output.txt'
    data_to_write = ''
    df_has_ranges = 'ranges' in df.columns.values

    # write A matrix
    if df_has_ranges:
        a_matrix_values = df.drop(['b', 'ranges'], axis=1)
        a_matrix_values_to_string = a_matrix_values.to_string(index=False, header=False, float_format='%.3f')
    else:
        a_matrix_values = df.drop('b', axis=1)
        a_matrix_values_to_string = a_matrix_values.to_string(index=False, header=False, float_format='%.3f')
    data_to_write += 'A=[ ' + a_matrix_values_to_string + ']\n\n'

    # write b vector
    b_vector = df[['b']]
    b_vector = b_vector.to_string(index=False, header=False, float_format='%.3f')
    data_to_write += 'b=[' + b_vector + ']\n\n'

    # write c vector
    c = a_matrix_values[a_matrix_values.index.str.startswith(objective__func_name)].to_string(
        index=False, header=False, float_format='%.3f')
    data_to_write += 'c=[' + '\n'.join(c.split()) + ']\n\n'

    # write c vector
    data_to_write += 'Eqin=[' + '\n'.join(eqin) + ']\n\n'

    # write MinMax
    data_to_write += 'MinMax={}\n\n'.format(min_max)

    # write ranges if exist
    if df_has_ranges:
        __r_data_from_df = df[['b', 'ranges']]
        __r_data_from_df.dropna(inplace=True)
        __r_data_from_df['rhs_range'] = __r_data_from_df['b'] + __r_data_from_df['ranges']
        __r_data_from_df['range_is_bigger'] = ['1' if _range > 0 else '-1' if _range < 0 else '0'
                                               for _range in __r_data_from_df['ranges']]
        __r_data_from_df.drop('ranges', axis=1, inplace=True)
        __r_data_from_df = __r_data_from_df.to_string(header=False, float_format='%d')
        data_to_write += 'R=[ ' + __r_data_from_df + ']\n\n'

    # write bounds if exist
    if len(bs_array):
        data_to_write += 'BS=[ ' + '\n'.join(' '.join(map(str, line)) for line in bs_array) + ']\n'

    with open(output_file_name, 'w') as f:
        f.write(data_to_write)


def main():
    # file_name = 'forplan.mps'
    file_name = sys.argv[1]

    # read file
    file_data = __read_file(file_name)

    # parse data
    handle_file_data(file_data)


if __name__ == '__main__':
    main()
