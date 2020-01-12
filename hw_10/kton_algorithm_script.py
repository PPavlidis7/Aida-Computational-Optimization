"""
    This is script applies kton algorithm in a mps file.
    In order to run: python Pavlidis_week(8) <file_name> <k_value>
"""
import numpy as np


def __apply_singleton(a_matrix_values, b_vector, c_vector, eqin, c0_value):
    """
    :param a_matrix_values: 2d ndarray
    :param b_vector: 1d ndarray
    :param c_vector: 1d ndarray
    :param eqin: 1d ndarray
    :param c0_value: float
    :return: 2d ndarray, 1d ndarray, 1d ndarray, 1d ndarray, float

    Apply singleton algorithm
    """
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
    """
    :param a_matrix_values: 2d ndarray,
    :param eqin: 1d ndarray,
    :param k_value: int
    :return: int, int

    Find the row index and the column index that we will apply kton
    """
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
    """
    :param a_matrix_values: 2d ndarray
    :param b_vector: 1d ndarray
    :param c_vector: 1d ndarray
    :param eqin: 1d ndarray
    :param c0_value: float
    :param k_value: int
    :return: 2d ndarray, 1d ndarray, 1d ndarray, 1d ndarray, float

    Apply kton algorithm
    """
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


def kton_algorithm(a_matrix_values, b_vector, c_vector, eqin, c0_value, k_value=4):
    if k_value == 1:
        a_matrix_values, b_vector, c_vector, eqin, c0_value = __apply_singleton(a_matrix_values, b_vector, c_vector, eqin, c0_value)
    else:
        a_matrix_values, b_vector, c_vector, eqin, c0_value = __apply_kton(a_matrix_values, b_vector, c_vector, eqin, c0_value, k_value)
    return a_matrix_values, b_vector, c_vector, eqin, c0_value
