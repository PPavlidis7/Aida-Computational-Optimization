import sys

import numpy as np
from mps_parser import parse_file


def __apply_singleton(a_matrix_values, b_vector, c_vector, eqin, c0_value):
    k_value = 1
    while k_value == 1:
        selected_row_index, line_most_right_nz_index = __select_line_index_to_apply_kton(a_matrix_values, eqin, k_value)
        if selected_row_index is None:
            break

        x_j = b_vector[selected_row_index]/a_matrix_values[selected_row_index][line_most_right_nz_index]
        if x_j < 0:
            print("The LP problem is infeasible")
            break

        b_vector -= x_j*a_matrix_values[:, line_most_right_nz_index]
        if c_vector[line_most_right_nz_index]:
            c0_value += c_vector[line_most_right_nz_index]*x_j

        # delete column and rows - update variables
        a_matrix_values = np.delete(a_matrix_values, line_most_right_nz_index, 1)
        a_matrix_values = np.delete(a_matrix_values, selected_row_index, 0)
        b_vector = np.delete(b_vector, selected_row_index)
        eqin = np.delete(eqin, selected_row_index)
        c_vector = np.delete(c_vector, line_most_right_nz_index)

    return a_matrix_values, b_vector, c_vector, eqin, c0_value


def __select_line_index_to_apply_kton(a_matrix_values, eqin, k_value):
    num_lines_nz = np.count_nonzero(a_matrix_values, axis=1)[::-1]
    selected_index = None
    line_most_right_nz_index = None
    for index, line_nz in enumerate(num_lines_nz):
        if line_nz == k_value:
            selected_index = len(num_lines_nz) - 1 - index
            if eqin[selected_index] != 0:
                selected_index = None
                continue
            selected_line = a_matrix_values[selected_index]
            line_most_right_nz_index = np.max(np.nonzero(selected_line))
            break
    return selected_index, line_most_right_nz_index


def __find_rows_to_change(a_matrix_values, column_index, selected_row_index):
    """
        Find the row indexes that has non zero value at column index and return these indexes. Do not include
        selected_row_index
    """
    return [row_index for row_index, row_values in enumerate(a_matrix_values) if row_values[column_index] and
            row_index != selected_row_index]


def __apply_kton(a_matrix_values, b_vector, c_vector, eqin, c0_value, k_value):
    k = k_value
    while k > 1:
        selected_row_index, line_most_right_nz_index = __select_line_index_to_apply_kton(a_matrix_values, eqin, k)
        if selected_row_index is None:
            k -= 1
            continue

        a_ij = a_matrix_values[selected_row_index][line_most_right_nz_index]
        b_vector[selected_row_index] /= a_ij
        a_matrix_values[selected_row_index] /= a_ij
        eqin[selected_row_index] = -1

        rows_to_change = __find_rows_to_change(a_matrix_values, line_most_right_nz_index, selected_row_index)
        for row_index in rows_to_change:
            b_vector[row_index] -= b_vector[selected_row_index] * a_matrix_values[row_index][line_most_right_nz_index]
            a_matrix_values[row_index] -= a_matrix_values[row_index][line_most_right_nz_index] * \
                                          a_matrix_values[selected_row_index]
        if c_vector[line_most_right_nz_index]:
            c0_value += c_vector[line_most_right_nz_index]*b_vector[selected_row_index]
            c_vector -= c_vector[line_most_right_nz_index]*a_matrix_values[selected_row_index]

        # delete columns - update variables
        a_matrix_values = np.delete(a_matrix_values, line_most_right_nz_index, 1)
        c_vector = np.delete(c_vector, line_most_right_nz_index)

    a_matrix_values, b_vector, c_vector, eqin, c0_value = __apply_singleton(a_matrix_values, b_vector, c_vector, eqin, c0_value)
    return a_matrix_values, b_vector, c_vector, eqin, c0_value


def main():
    # file_name = sys.argv[1]
    # k_value = sys.argv[2]

    file_name = 'afiro.mps'
    k_value = 4

    a_matrix_values, b_vector, c_vector, eqin, c0_value, min_max = parse_file(file_name)
    # a_matrix_values, b_vector, c_vector, eqin, c0_value, min_max = get_mock_data()

    if k_value == 1:
        a_matrix_values, b_vector, c_vector, eqin, c0_value = __apply_singleton(a_matrix_values, b_vector, c_vector, eqin, c0_value)
    else:
        a_matrix_values, b_vector, c_vector, eqin, c0_value = __apply_kton(a_matrix_values, b_vector, c_vector, eqin, c0_value, k_value)


def get_mock_data():
    a_matrix = np.asarray([
                [0.0, 3.0, 0.0, 0.0],
                [4.0, -3.0, 8.0, -1.0],
                [-3.0, 2.0, 0.0, -4.0],
                [4.0, 0.0, -1.0, 0.0]
    ])
    b = np.asarray([6.0, 20.0, -8.0, 18.0])
    c = np.asarray([-2.0, 4.0, -2.0, 2.0])
    eqin = np.asarray([0, 0, 0, 0])
    c0 = 0
    min_max = 1
    return a_matrix, b, c, eqin, c0, min_max


if __name__ == '__main__':
    main()
