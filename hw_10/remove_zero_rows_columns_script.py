"""
    This is script applies arithmetic mean method in a mps file.
    In order to run: python Pavlidis_week(8) <file_name>
"""
import numpy as np


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


def remove_zero_rows_columns(a_matrix_values, b_vector, c_vector, eqin, c0_value):
    a_matrix_values, b_vector, c_vector, eqin, not_infeasible_or_unbounded = \
        __remove_zero_rows_columns(a_matrix_values, b_vector, c_vector, eqin)
    return a_matrix_values, b_vector, c_vector, eqin, not_infeasible_or_unbounded
