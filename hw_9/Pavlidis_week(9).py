"""
    This is script applies arithmetic mean method in a mps file.
    In order to run: python Pavlidis_week(8) <file_name>
"""
import sys

import numpy as np
from mps_parser import parse_file


def __remove_zero_rows(a_matrix_values, b_vector, eqin):
    """
    :param a_matrix_values: 2d ndarray
    :param b_vector: 1d ndarray
    :param eqin: 1d ndarray
    :return: 2d ndarray, 1d ndarray, 1d ndarray

    Remove zero rows from a_matrix and make the appropriate changes at b_vector and eqin
    """
    find_zero_row = False
    lines_zero_indexes = np.where(~a_matrix_values.any(axis=1))[0][::-1]
    for row_index in lines_zero_indexes:
        if (eqin[row_index] == -1 and b_vector[row_index] < 0) \
                or (eqin[row_index] == 1 and b_vector[row_index] > 0) \
                or (eqin[row_index] == 0 and b_vector[row_index] != 0):
            print("The LP problem is infeasible")
            return a_matrix_values, b_vector, eqin, None
        else:
            find_zero_row = True
            a_matrix_values = np.delete(a_matrix_values, row_index, 0)
            b_vector = np.delete(b_vector, row_index)
            eqin = np.delete(eqin, row_index)
    return a_matrix_values, b_vector, eqin, find_zero_row


def __remove_zero_columns(a_matrix_values, c_vector):
    """
    :param a_matrix_values: 2d ndarray
    :param c_vector: 1d ndarray
    :return: 2d ndarray, 1d ndarray

    Remove zero columns from a_matrix and make the appropriate changes at c_vector
    """
    find_zero_column = False
    column_zero_indexes = np.where(~a_matrix_values.any(axis=0))[0][::-1]
    for col_index in column_zero_indexes:
        if c_vector[col_index] < 0:
            print("The LP problem is unbounded")
            return a_matrix_values, c_vector, None
        else:
            find_zero_column = True
            a_matrix_values = np.delete(a_matrix_values, col_index, 1)
            c_vector = np.delete(c_vector, col_index)
    return a_matrix_values, c_vector, find_zero_column


def __remove_zero_rows_columns(a_matrix_values, b_vector, c_vector, eqin):
    """
    :param a_matrix_values: 2d ndarray
    :param b_vector: 1d ndarray
    :param c_vector: 1d ndarray
    :param eqin: 1d ndarray
    :return: 2d ndarray, 1d ndarray, 1d ndarray, 1d ndarray

    Run until a_matrix has no empty columns and rows
    """
    find_zero_row = True
    find_zero_column = True
    while find_zero_row or find_zero_column:
        a_matrix_values, b_vector, eqin, find_zero_row = __remove_zero_rows(a_matrix_values, b_vector, eqin)
        if find_zero_row is None:
            break

        a_matrix_values, c_vector, find_zero_column = __remove_zero_columns(a_matrix_values, c_vector)
        if find_zero_column is None:
            break
    else:
        return a_matrix_values, b_vector, c_vector, eqin, True
    return a_matrix_values, b_vector, c_vector, eqin, False


def _calculate_r_vector(a_matrix, b_vector):
    """
    :param a_matrix: 2d ndarray
    :param b_vector: 1d ndarray
    :return: 2d ndarray, 1d ndarray

    Find and return r_vector and apply scaling at a_matrix and b_vector
    """
    r_vector = []
    for row_index, row_values in enumerate(a_matrix):
        num_lines_nz = np.count_nonzero(row_values, axis=0)
        if np.sum(row_values) ==0:
            raise ValueError('There are zero rows')
        r_row_value = num_lines_nz/np.sum(row_values)
        r_vector.append(r_row_value)
        a_matrix[row_index] = a_matrix[row_index] * r_row_value
    b_vector = np.multiply(b_vector, r_vector)
    return np.asarray(r_vector)


def __calculator_s_vector(a_matrix, c_vector):
    """
    :param a_matrix: 2d ndarray
    :param c_vector: 1d ndarray
    :return: 2d ndarray, 1d ndarray

    Find and return s_vector and apply scaling at a_matrix and c_vector
    """
    s_vector = []
    for column_index, column_values in enumerate(a_matrix.T):
        num_column_nz = np.count_nonzero(column_values, axis=0)
        s_column_value = num_column_nz/np.sum(column_values)
        s_vector.append(s_column_value)
        a_matrix[:, column_index] = a_matrix[:, column_index] * s_column_value
    c_vector = np.multiply(c_vector, s_vector)
    return np.asarray(s_vector)


def __arithmetic_mean_scaling(a_matrix_values, b_vector, c_vector):
    """
    :param a_matrix_values: 2d ndarray
    :param b_vector: 1d ndarray
    :param c_vector: 1d ndarray
    :return: 1d ndarray, 1d ndarray

    Find r_vector and s_vector and apply arithmetic mean method at a_matrix_values, b_vector and c_vector
    """
    r_vector = _calculate_r_vector(a_matrix_values, b_vector)
    s_vector = __calculator_s_vector(a_matrix_values, c_vector)
    return r_vector, s_vector


def main():
    if len(sys.argv) < 2:
        raise ValueError('Wrong input. Expected: python Pavlidis_week(8) <file_name>')
    else:
        file_name = sys.argv[1]

    # a_matrix_values, b_vector, c_vector, eqin, c0_value, min_max = parse_file(file_name)
    a_matrix_values, b_vector, c_vector, eqin, c0_value, min_max = get_mock_data()

    if min_max == 1:
        c_vector = c_vector * (-1)

    a_matrix_values, b_vector, c_vector, eqin, not_infeasible_or_unbounded = \
        __remove_zero_rows_columns(a_matrix_values, b_vector, c_vector, eqin)
    if not_infeasible_or_unbounded:
        r_vector, s_vector = __arithmetic_mean_scaling(a_matrix_values, b_vector, c_vector)

        print('a_matrix = \n', a_matrix_values)
        print('b_vector = ', b_vector)
        print('c_vector =', c_vector)
        print('eqin = ', eqin)
        print('r_vector', r_vector)
        print('s_vector = ', s_vector)


def get_mock_data():
    """
        A helper function in order to mock user's input
    """
    # a_matrix = np.asarray([
    #     [1.0, -4.0, 0.0, 0.0, 3.0],
    #     [-1.0, 2.0, 5.0, 0.0, -2.0],
    #     [0.0, 0.0, 0.0, 0.0, 0.0],
    #     [5.0, 4.0, 3.0, 0.0, -2.0]
    # ])
    # b = np.asarray([12.0, 2.0, -5.0, 7.0])
    # c = np.asarray([-1.0, 4.0, 5.0, -2.0, 8.0, 2.0])
    # eqin = np.asarray([-1, 1, 0, 0, 0])

    # a_matrix = np.asarray([
    #     [2.0, -3.0, 0.0, 0.0, 3.0, 1.0],
    #     [-1.0, 3.0, 2.0, 0.0, -1.0, -2.0],
    #     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    #     [7.0, 5.0, 2.0, 0.0, -2.0, 4.0],
    #     [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    # ])
    # b = np.asarray([9.0, 1.0, -5.0, 7.0, -10.0])
    # c = np.asarray([-1.0, 4.0, 5.0, -2.0, 8.0, 2.0])
    # eqin = np.asarray([-1, 1, 1, 0, 1])

    a_matrix = np.asarray([
        [956, 0.0, 1.0, 258/5],
        [5/2, 4.0, 13/2, 149/5],
        [1, 3/2, 0.0, 67/10]
    ])
    c = np.asarray([7/2, 0.0, 453.0, 6.0])
    b = np.asarray([4.0, 7/2, 55.0])
    eqin = np.asarray([0, 0, 0])

    c0 = 0
    min_max = -1
    return a_matrix, b, c, eqin, c0, min_max


if __name__ == '__main__':
    main()
