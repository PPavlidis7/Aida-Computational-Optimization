"""
    This is script solve a problem from a mps file using exterior point algorithm.
    In order to run: python Pavlidis_week(10) <file_name>
"""
import sys
from scipy.optimize import linprog
import numpy as np
from mps_parser import parse_file
import random


TOLERANCE = 10 ** (-10)


def convert_constraints_to_equal(a_matrix_values, c_vector, eqin):
    c_vector = list(c_vector)
    vars_added = 0
    for constraint_index, constraint_value in enumerate(eqin):
        if constraint_value:
            eqin[constraint_index] = 0
            tmp_column = np.zeros(len(eqin))
            vars_added += 1
            if constraint_value == -1:
                tmp_column[constraint_index] = 1
            else:
                tmp_column[constraint_index] = -1
            a_matrix_values = np.concatenate([a_matrix_values, np.transpose([tmp_column])], axis=1)
            c_vector.append(0)
    return a_matrix_values, np.asarray(c_vector), eqin, vars_added


def init_b_n(a_matrix_values, num_b_indexes_to_select, vars_added):
    while True:
        indexes = random.choices(range(a_matrix_values.shape[1] - vars_added), k=num_b_indexes_to_select - vars_added) \
                  + list(range(a_matrix_values.shape[1] - vars_added, a_matrix_values.shape[1]))
        values = a_matrix_values[:, indexes]
        if np.linalg.det(values) != 0:
            break
    b = {
        'values': values,
        'indexes': indexes,
    }
    b['inverse'] = np.linalg.inv(b['values'])
    n = {
        'values': a_matrix_values[:, :a_matrix_values.shape[1]-num_b_indexes_to_select],
        'indexes': list(set(range(a_matrix_values.shape[1])).difference(set(indexes)))
    }
    return b, n


# def init_b_n(a_matrix_values, num_b_indexes_to_select, vars_added):
#     """
#         For first example
#     """
#     b = {
#         'values': np.asarray(a_matrix_values[:, -num_b_indexes_to_select:]),
#         'indexes': list(range(a_matrix_values.shape[1]-num_b_indexes_to_select, a_matrix_values.shape[1])),
#     }
#     b['inverse'] = np.linalg.inv(b['values'])
#     n = {
#         'values': a_matrix_values[:, :a_matrix_values.shape[1]-num_b_indexes_to_select],
#         'indexes': list(range(a_matrix_values.shape[1]-num_b_indexes_to_select))
#     }
#     return b, n


# def init_b_n(a_matrix_values, num_b_indexes_to_select, vars_added):
#     """
#         For second example
#     """
#     b = {
#         'values': np.asarray(a_matrix_values[:, [0, 1]]),
#         'indexes': [0, 1],
#     }
#     b['inverse'] = np.linalg.inv(b['values'])
#     n = {
#         'values': a_matrix_values[:, [2, 3]],
#         'indexes': [2, 3]
#     }
#     return b, n


def calculate_new_b_n(a_matrix_values, b, n):
    b['values'] = a_matrix_values[:, b['indexes']]
    b['inverse'] = np.linalg.inv(b['values'])
    n['values'] = a_matrix_values[:, n['indexes']]


def calculate_w(c_vector, b):
    c_b = c_vector[b['indexes']]
    return np.dot(c_b, b['inverse'])


def calculate_sn(c_vector, b, n):
    w = calculate_w(c_vector, b)
    c_n = c_vector[n['indexes']]
    return c_n - np.dot(w, n['values'])


def calculate_xb(b_vector, b):
    return np.dot(b['inverse'], b_vector)


def calculate_d_b(a_matrix, b, p):
    return -np.sum(np.dot(b['inverse'], a_matrix[:, p]), axis=1)


def calculate_z(c_vector, x_b, b):
    return np.dot(c_vector[b['indexes']], x_b)


def phase_two(a_matrix_values, b_vector, c_vector, c0_value, s_n, p_set, x_b, d_b, b, n):
    q_set = [index for index, value in enumerate(s_n) if value >= 0]
    s_0 = np.sum(s_n[[index for index, value in enumerate(n['indexes']) if value in p_set]])
    count_iterations = 0
    while len(p_set):
        if all(value >= 0 for value in d_b) and s_0 == 0:
            # LP is optimal
            z = calculate_z(c_vector, x_b, b) + c0_value
            print(x_b, z)
            return x_b, z
        else:
            x_b_divided_d_b = [(x_b[index] / abs(value)) for index, value in enumerate(d_b) if value < 0]
            if not len(x_b_divided_d_b):
                print("The LP is unbounded")
                break
            r = x_b_divided_d_b.index(min(x_b_divided_d_b))
            k = b['indexes'][r]
            HrP = np.dot(b['inverse'][r], a_matrix_values[:, p_set])
            HrQ = []
            if len(q_set):
                HrQ = np.dot(b['inverse'][r], a_matrix_values[:, q_set])
            # ratios
            theta_1_value, theta_1_index = calculate_theta_1(HrP, p_set, s_n, n)
            theta_2_value, theta_2_index = calculate_theta_2(HrQ, q_set, s_n, n)
            # set l = entering_var
            # theta_1_index = t1 and theta_2_index = t2
            if theta_1_value == theta_2_value and theta_1_value == np.inf:
                raise ValueError("theta_1 == theta_2 == inf")
            if theta_1_value <= theta_2_value:
                entering_var = p_set[theta_1_index]
                p_set.remove(p_set[theta_1_index])
                q_set.append(k)
            else:
                entering_var = q_set[theta_2_index]
                q_set[theta_2_index] = k

            n['indexes'] = p_set + q_set
            b['indexes'][r] = entering_var
            calculate_new_b_n(a_matrix_values, b, n)
            s_n = calculate_sn(c_vector, b, n)
            x_b = calculate_xb(b_vector, b)
            h_j = np.dot(b['inverse'], a_matrix_values[:, p_set])
            d_b = -h_j.sum(axis=1)
            count_iterations += 1
            # x = 1
    else:
        z = calculate_z(c_vector, x_b, b)
        print(x_b, z)
        return x_b, z + c0_value

    # x = 1


def calculate_theta_1(HrP, p_set, s_n, n):
    theta_value = None
    theta_index = None
    # find p indexes in s_n
    s_n_indexes_belong_to_p_set = [index for index, value in enumerate(n['indexes']) if value in p_set]
    for hrp_index, hrp_value in enumerate(HrP):
        if hrp_value > 0 and hrp_index < len(s_n_indexes_belong_to_p_set):
            tmp = -s_n[s_n_indexes_belong_to_p_set[hrp_index]]/hrp_value
            if theta_value is None or tmp < theta_value:
                theta_value = tmp
                theta_index = hrp_index
    if theta_value is None:
        theta_value = np.inf
    return theta_value, theta_index


def calculate_theta_2(HrQ, q_set, s_n, n):
    theta_value = None
    theta_index = None
    # find q indexes in s_n
    s_n_indexes_belong_to_q_set = [index for index, value in enumerate(n['indexes']) if value in q_set]
    for hrq_index, hrq_value in enumerate(HrQ):
        if hrq_value < 0 and hrq_index < len(s_n_indexes_belong_to_q_set):
            tmp = -s_n[s_n_indexes_belong_to_q_set[hrq_index]]/hrq_value
            if theta_value is None or tmp < theta_value:
                theta_value = tmp
                theta_index = hrq_index
    if theta_value is None:
        theta_value = np.inf
    return theta_value, theta_index


def main():
    # if len(sys.argv) < 2:
    #     raise ValueError('Wrong input. Expected: python Pavlidis_week(10) <file_name>')
    # else:
    #     file_name = sys.argv[1]

    file_name = 'sdata1_100x100.mps'
    a_matrix_values, b_vector, c_vector, eqin, c0_value, min_max = parse_file(file_name)
    # a_matrix_values, b_vector, c_vector, eqin, c0_value, min_max = get_mock_data()

    if min_max == 1:
        c_vector = c_vector * (-1)

    a_matrix_values, c_vector, eqin, vars_added = convert_constraints_to_equal(a_matrix_values, c_vector, eqin)
    num_b_indexes_to_select = len(eqin)
    b, n = init_b_n(a_matrix_values, num_b_indexes_to_select, vars_added)
    s_n = calculate_sn(c_vector, b, n)
    p_set = [n['indexes'][index] for index, value in enumerate(s_n) if value < 0]
    x_b = calculate_xb(b_vector, b)
    d_b = calculate_d_b(a_matrix_values, b, p_set)
    greek_b = max([(x_b[index] / -d_b[index]) for index, value in enumerate(x_b) if value < 0], default=-np.inf)
    greek_a = min([(x_b[index] / -d_b[index]) for index, value in enumerate(d_b) if value < 0], default=np.inf)

    if not len(p_set) or greek_b > greek_a:
        raise NotImplementedError('Problem {} needs phase 1'.format(file_name))

    # noinspection SpellCheckingInspection,PyTypeChecker
    __scipy_solution = linprog(c_vector, A_eq=a_matrix_values, b_eq=b_vector, method='revised simplex')
    print(__scipy_solution)
    print('-'*10)
    phase_two(a_matrix_values, b_vector, c_vector, c0_value, s_n, p_set, x_b, d_b, b, n)

    # x = 1


def get_mock_data():
    """
        A helper function in order to mock user's input
    """
    """
        first example
    """
    # a_matrix = np.asarray([
    #     [1.0, 2.0, 1.0, 3.0],
    #     [-4.0, 1.0, -2.0, 1.0],
    #     [3.0, -2.0, -1.0, 2.0],
    # ])
    # b = np.asarray([12.0, -4.0, 8.0])
    # c = np.asarray([-2.0, 1.0, -3.0, -1.0])
    # eqin = np.asarray([-1, 1, -1])

    """
        second example
    """
    a_matrix = np.asarray([
        [2.0, 0.0, 2.0, 3.0],
        [0.0, -2.0, -2.0, -6.0],
    ])
    b = np.asarray([10.0, -6.0])
    c = np.asarray([1.0, 0.0, -1.0, -3.0])
    eqin = np.asarray([0, 0])

    c0 = 0
    min_max = -1
    return a_matrix, b, c, eqin, c0, min_max


if __name__ == '__main__':
    main()
