from libsim import config
config.use_cache = True
config.debug = 1

import libsim.numpy as np

# --- 1.1 Creating from a list ---
data = [1, 2, 3, 4, 5]
arr1d = np.array(data)

# Assertions for a 1D array
assert isinstance(arr1d, np.ndarray)
assert arr1d.shape == (5,)
assert arr1d.ndim == 1
assert arr1d.size == 5
assert arr1d.dtype == np.int64 or arr1d.dtype == np.int32 # Dtype can be platform-dependent
assert arr1d[2] == 3

# --- 1.2 Creating a 2D array (matrix) ---
matrix_data = [[1, 2, 3], [4, 5, 6]]
matrix = np.array(matrix_data, dtype=np.float32)

# Assertions for a 2D array
assert matrix.shape == (2, 3)
assert matrix.ndim == 2
assert matrix.size == 6
assert matrix.dtype == np.float32

# --- 1.3 Using creation functions ---
# np.arange
range_arr = np.arange(10) # 0 to 9
assert range_arr.shape == (10,)
assert range_arr[0] == 0
assert range_arr[-1] == 9
assert np.array_equal(range_arr, np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]))

# np.zeros
zeros_arr = np.zeros((3, 4))
assert zeros_arr.shape == (3, 4)
assert zeros_arr.dtype == np.float64 # Default is float
assert np.all(zeros_arr == 0) # Check if all elements are 0

# np.ones
ones_arr = np.ones(5, dtype=np.int8)
assert ones_arr.shape == (5,)
assert ones_arr.dtype == np.int8
assert np.sum(ones_arr) == 5

# np.linspace (linearly spaced points)
linspace_arr = np.linspace(0, 1, 5) # 5 points from 0 to 1 (inclusive)
assert linspace_arr.size == 5
assert linspace_arr[0] == 0.0
assert linspace_arr[-1] == 1.0
# For floating point comparisons, use np.isclose or np.allclose
assert np.isclose(linspace_arr[2], 0.5)
assert np.allclose(linspace_arr, np.array([0.0, 0.25, 0.5, 0.75, 1.0]))

# np.eye (identity matrix)
identity_matrix = np.eye(3)
assert identity_matrix.shape == (3, 3)
assert np.trace(identity_matrix) == 3.0 # Sum of diagonal is 3
assert identity_matrix[1, 1] == 1.0
assert identity_matrix[1, 2] == 0.0

print("✅ Section 1: Array Creation and Attributes assertions passed!")

arr = np.arange(12).reshape(3, 4)
# [[ 0,  1,  2,  3],
#  [ 4,  5,  6,  7],
#  [ 8,  9, 10, 11]]

# --- 2.1 Single element access ---
assert arr[0, 0] == 0
assert arr[1, 2] == 6
assert arr[-1, -1] == 11 # Negative indexing

# --- 2.2 Slicing ---
# Get the first row
first_row = arr[0, :]
assert first_row.shape == (4,)
assert np.array_equal(first_row, np.array([0, 1, 2, 3]))

# Get the second column
second_col = arr[:, 1]
assert second_col.shape == (3,)
assert np.array_equal(second_col, np.array([1, 5, 9]))

# Get a sub-matrix (top-left 2x2)
sub_matrix = arr[:2, :2]
assert sub_matrix.shape == (2, 2)
assert np.array_equal(sub_matrix, np.array([[0, 1], [4, 5]]))

# --- 2.3 Fancy Indexing (indexing with lists/arrays) ---
rows_to_get = [0, 2]
fancy_indexed = arr[rows_to_get, :] # Get 1st and 3rd row
assert fancy_indexed.shape == (2, 4)
assert np.array_equal(fancy_indexed, np.array([[0, 1, 2, 3], [8, 9, 10, 11]]))

cols_to_get = [0, 3]
fancy_indexed_cols = arr[:, cols_to_get]
assert np.array_equal(fancy_indexed_cols, np.array([[0, 3], [4, 7], [8, 11]]))


print("✅ Section 2: Indexing and Slicing assertions passed!")

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# --- 3.1 Element-wise operations ---
c_add = a + b
assert np.array_equal(c_add, np.array([5, 7, 9]))

c_mul = a * b
assert np.array_equal(c_mul, np.array([4, 10, 18]))

# --- 3.2 Scalar operations ---
d = a * 10
assert np.array_equal(d, np.array([10, 20, 30]))

# --- 3.3 Ufuncs (sqrt, exp, sin, etc.) ---
sqrt_arr = np.sqrt(np.array([4, 9, 16]))
assert sqrt_arr.dtype == np.float64
assert np.allclose(sqrt_arr, np.array([2., 3., 4.]))

exp_arr = np.exp(np.array([0, 1]))
assert np.allclose(exp_arr, np.array([1., np.e]))

# --- 3.4 Broadcasting ---
# A key concept to verify with asserts
matrix = np.arange(6).reshape(2, 3) # [[0, 1, 2], [3, 4, 5]]
row_vector = np.array([10, 20, 30])

# Broadcast the row_vector to each row of the matrix
broadcasted_sum = matrix + row_vector
assert broadcasted_sum.shape == matrix.shape
assert np.array_equal(broadcasted_sum, np.array([[10, 21, 32], [13, 24, 35]]))

col_vector = np.array([[100], [200]]) # Shape (2, 1)
broadcasted_sum_col = matrix + col_vector
assert broadcasted_sum_col.shape == matrix.shape
assert np.array_equal(broadcasted_sum_col, np.array([[100, 101, 102], [203, 204, 205]]))

print("✅ Section 3: Mathematical Operations assertions passed!")

data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# --- 4.1 Whole array aggregations ---
assert data.sum() == 45
assert data.min() == 1
assert data.max() == 9
assert np.isclose(data.mean(), 5.0)
assert np.isclose(data.std(), 2.58198889747)

# --- 4.2 Aggregations along an axis ---
# Sum along columns (axis=0)
col_sums = data.sum(axis=0)
assert col_sums.shape == (3,)
assert np.array_equal(col_sums, np.array([12, 15, 18]))

# Mean along rows (axis=1)
row_means = data.mean(axis=1)
assert row_means.shape == (3,)
assert np.allclose(row_means, np.array([2.0, 5.0, 8.0]))

print("✅ Section 4: Aggregations and Statistics assertions passed!")

arr = np.arange(12)

# --- 5.1 Reshaping ---
reshaped_arr = arr.reshape(4, 3)
assert reshaped_arr.shape == (4, 3)
assert arr.size == reshaped_arr.size # The number of elements must not change
assert reshaped_arr[3, 2] == 11

# --- 5.2 Transposing ---
matrix = np.array([[1, 2], [3, 4], [5, 6]]) # Shape (3, 2)
transposed = matrix.T
assert transposed.shape == (2, 3)
assert matrix[1, 0] == transposed[0, 1]
assert np.array_equal(transposed, np.array([[1, 3, 5], [2, 4, 6]]))

# --- 5.3 Stacking ---
a = np.array([1, 1])
b = np.array([2, 2])
vstacked = np.vstack((a, b)) # Vertical stack
assert vstacked.shape == (2, 2)
assert np.array_equal(vstacked, np.array([[1, 1], [2, 2]]))

hstacked = np.hstack((a, b)) # Horizontal stack
assert hstacked.shape == (4,)
assert np.array_equal(hstacked, np.array([1, 1, 2, 2]))

# --- 5.4 Splitting ---
long_arr = np.arange(10)
split_arrs = np.split(long_arr, [3, 7]) # Split at indices 3 and 7
assert len(split_arrs) == 3
assert np.array_equal(split_arrs[0], np.array([0, 1, 2]))
assert np.array_equal(split_arrs[1], np.array([3, 4, 5, 6]))
assert np.array_equal(split_arrs[2], np.array([7, 8, 9]))


print("✅ Section 5: Array Manipulation assertions passed!")


data = np.arange(10)

# --- 6.1 Boolean Masking ---
mask = data > 5
assert mask.dtype == bool
assert mask.shape == data.shape
assert np.array_equal(mask, np.array([F, F, F, F, F, F, T, T, T, T])) # F = False, T = True

# --- 6.2 Boolean Indexing ---
filtered_data = data[mask]
assert np.all(filtered_data > 5)
assert np.array_equal(filtered_data, np.array([6, 7, 8, 9]))

# --- 6.3 np.where (ternary operator) ---
# If value > 5, use the value, otherwise use -1
result = np.where(data > 5, data, -1)
assert np.array_equal(result, np.array([-1, -1, -1, -1, -1, -1, 6, 7, 8, 9]))

# --- 6.4 np.any and np.all ---
bools = np.array([True, False, True])
assert np.any(bools) == True
assert np.all(bools) == False

assert not np.all(data > 8)
assert np.any(data == 7)

print("✅ Section 6: Logical Operations assertions passed!")


A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# --- 7.1 Matrix Multiplication ---
# In Python 3.5+, @ is the infix operator for matrix multiplication
C = A @ B
# Expected: [[1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]]
#         = [[19, 22], [43, 50]]
assert C.shape == (2, 2)
assert np.array_equal(C, np.array([[19, 22], [43, 50]]))

# --- 7.2 Matrix Inverse ---
A_inv = np.linalg.inv(A)
# The key property: A @ A_inv should be the identity matrix
identity = A @ A_inv
assert np.allclose(identity, np.eye(2))

# --- 7.3 Determinant ---
det_A = np.linalg.det(A)
# Expected: 1*4 - 2*3 = -2
assert np.isclose(det_A, -2.0)

print("✅ Section 7: Linear Algebra assertions passed!")