from typing import Union

from .errors import SizeMismatchError, NonsquareMatrixError
from .scalar import Scalar
from .vector import Vector


class Matrix:
    """A Matrix is an N * M array of vectors that describe a linear system

    :param vectors: The list of Vectors to instantiate the Matrix with
    :param transposed: Whether or not the Matrix should be transposed
    """

    @staticmethod
    def identity(m: int):
        """Returns an m * m identity matrix

        :param m: The size of the matrix
        """
        return Matrix([
            Vector([ 1 if i == j else 0 for j in range(m) ]) 
            for i in range(m)
        ])
        
    @staticmethod
    def __determinant(matrix: 'Matrix'=None) -> 'Scalar':
        """A helper function to calculate the determinant 
        of the specified square Matrix recursively

        :param matrix: The matrix to retrieve the determinant of
        """
        
        # This can only be done on square matrices
        if matrix.width == matrix.height:
            
            # The 2 x 2 matrix is the base case for this recursive function
            #   simply do the determinant using (x1y2 - x2y1)
            if matrix.width == 2:
                return (matrix[0][0] * matrix[1][1]) - (matrix[0][1] * matrix[1][0])
            
            # If the Matrix is larger than a 2 x 2, retrieve a subportion of the specified Matrix
            #   by creating another Matrix containing the Vectors that do not include the Scalar
            #   being multiplied by (the first Scalar of each Vector in the Matrix)
            else:
                submatrices = [
                    matrix.subsquare(i, 0)
                    for i in range(len(matrix))
                ]
                
                # Iterate through each submatrix and add the results together in an
                #   alternating a + b - c + d - ... ∞
                determinant = Scalar(0)
                for x in range(len(submatrices)):
                    if x % 2 == 0:  # Add
                        determinant += matrix[x][0] * submatrices[x].determinant()
                    else:           # Subtract
                        determinant -= matrix[x][0] * submatrices[x].determinant()
                return determinant
                        
        raise NonsquareMatrixError()
    
    @staticmethod
    def linear_regression(vectors: list) -> 'Vector':
        """Returns the Vector for [ m b ] for y = mx + b
        to find the linear regression for a Matrix of Vectors in R2

        :param vectors: A list of Vectors to use to find the linear regression
        """
        for vector in vectors:
            if len(vector) > 2:
                raise SizeMismatchError()

        # Create a Matrix for the x values and a Vector for the y values
        matrix = Matrix([
            # Add a vector of the x values of each vector
            Vector([ v[0] for v in vectors ])
        ] + [
            # Add a vector of 1's to the matrix
            Vector([ 1 for v in vectors ])
        ])
        vector = Matrix([
            Vector([ 
                v[1] for v in vectors
            ])
        ])

        # Get the results of the Matrix multiplied by itself, transposed
        #   and get the inverse of that
        aTa_1 = (matrix.transpose() * matrix).inverse()
        aTy   = matrix.transpose() * vector
        
        return aTa_1 * aTy

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, vectors: list):
        for i in range(1, len(vectors)):
            if len(vectors[0]) != len(vectors[i]):
                raise SizeMismatchError()
        self.__vectors = vectors
        self.__rows = len(vectors[0])
        self.__columns = len(vectors)

        # Iterate through each vector to add it to the matrix list
        length = 0
        for r in range(self.height):
            for c in range(self.width):
                if len(str(self.__vectors[c][r])) > length:
                    length = len(str(self.__vectors[c][r]))

        # Iterate through each row of each Vector to add it
        #   to the string as a transposed string and a regular string
        string = ""
        for r in range(self.height):
            substring = ""
            for c in range(self.width):
                substring += f" {str(self.__vectors[c][r]).center(length)} "
            string += f"| {substring} |\n"
        self.__string = string

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __str__(self) -> str:
        return self.__string

    def __eq__(self, matrix: 'Matrix') -> bool:
        if self.width != matrix.width or self.height != matrix.height:
            return False
        for vector in range(len(self)):
            if self[vector] != matrix[vector]:
                return False
        return True

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __getitem__(self, index: int) -> int:
        return self.__vectors[index]

    def __len__(self) -> int:
        return len(self.__vectors)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __add__(self, matrix: 'Matrix') -> 'Matrix':
        """Adds two matrices together. Each matrix must be the same size

        :param matrix: The matrix to add to this matrix
        """

        # Check if the sizes of the matrices match
        if self.width == matrix.width and self.height == matrix.height:
            return Matrix([
                Vector(
                    [self[i][j] + matrix[i][j] for j in range(len(self[i]))])
                for i in range(len(self))
            ])
        raise SizeMismatchError()

    def __sub__(self, matrix: 'Matrix') -> 'Matrix':
        """Subtracts two matrices. Each matrix must be the same size

        :param matrix: The matrix to subtract from this matrix
        """

        # Check if the sizes of the matrices match
        if self.width == matrix.width and self.height == matrix.height:
            return Matrix([
                Vector(
                    [self[i][j] - matrix[i][j] for j in range(len(self[i]))])
                for i in range(len(self))
            ])
        raise SizeMismatchError()

    def __mul__(self, matrix: Union['Matrix', 'Scalar', int]) -> ['Matrix', 'Scalar']:
        """Multiplies two matrices together or multiplies a matrix by a scalar. 
        The amount of rows of this matrix must match the amount of 
        columns of the specified matrix

        :param matrix: The matrix or scalar to multiply with this matrix
        """

        # Check if the specified Matrix is actually a Scalar
        if isinstance(matrix, (Scalar, int)):
            return Matrix([
                Vector([
                    self[i][j] * matrix
                    # Iterate through the scalars in each vector
                    for j in range(len(self[i]))
                ])
                # Iterate through the vectors of this matrix
                for i in range(len(self))
            ])

        # Check if the width of this matrix matches
        #   the height of the specified matrix
        if self.width == matrix.height:
            return Matrix([
                Vector([
                    sum([
                        self[k][i] * matrix[j][k]
                        # Iterate through the amount of rows in the specified matrix
                        #   which also equals the amount of columns in this matrix
                        for k in range(len(self))
                    ])
                    # Iterate through the amount of rows of this matrix
                    for i in range(len(self[0]))
                ])
                # Iterate through the amount of columns of the specified matrix
                for j in range(len(matrix))
            ])
        raise SizeMismatchError()
    
    def __rmul__(self, matrix: Union['Matrix', 'Scalar', int]) -> 'Matrix':
        """Multiplies two matrices together or multiplies a matrix by a scalar. 
        The amount of rows of this matrix must match the amount of 
        columns of the specified matrix

        :param matrix: The matrix or scalar to multiply with this matrix
        """
        return self * matrix
    
    def __neg__(self) -> 'Matrix':
        """Returns the Matrix after negating it (multiplying by -1)"""
        return self * -1

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def width(self) -> int:
        """Retrieves the width of this matrix"""
        return len(self.__vectors)

    @property
    def height(self) -> int:
        """Retrieves the height of this matrix"""
        return len(self.__vectors[0])

    @property
    def vectors(self) -> list:
        """Retrieves a list of Vectors in this Matrix"""
        return self.__vectors

    def is_transposed(self) -> bool:
        """Returns whether or not this Matrix is transposed"""
        return self.__transposed
    
    def is_square(self) -> bool:
        """Returns whether or not this Matrix is a square Matrix"""
        return self.width == self.height

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def transpose(self) -> 'Matrix':
        """Returns a transposed version of this Matrix"""
        return Matrix([
            Vector([self[j][i] for j in range(self.width)])
            for i in range(self.height)
        ])

    def extend(self, matrix: 'Matrix' = None, *,
               vector: Vector = None) -> 'Matrix':
        """Adds more vectors to this Matrix and returns a copy"""
        if matrix is not None:
            return Matrix([v for v in (self.vectors + matrix.vectors)])
        elif vector is not None:
            return Matrix([v for v in (self.vectors + [vector])])
        raise ValueError(
            "You must specify either a matrix or a vector to extend")

    def trim(self, vectors: int, *, start: bool = False) -> 'Matrix':
        """Trims this Matrix of the specified amount of vectors
        
        :param vectors: The amount of vectors to remove
        :param start: Whether to trim the start or the end of the matrix
        """
        if start:
            return Matrix(self.vectors[:vectors])
        return Matrix(self.vectors[vectors:])
    
    def subsquare(self, i: int, j: int) -> 'Matrix':
        """Returns a submatrix of values ignoring the i-th column
        and the j-th row

        :param i: The column to ignore
        :param j: The row to ignore
        """
        vectors = []
        for x in range(self.width):
            if x == i: continue
            vector = []
            for y in range(self.height):
                if y == j: continue
                vector.append(self[x][y])
            vectors.append(Vector(vector))
        return Matrix(vectors)
    
    def swap_vectors(self, i: int, j: int):
        """Swaps two vectors in this Matrix

        :param i: A vector to swap
        :param j: Another vector to swap
        """
        self.__vectors[i], self.__vectors[j] = self.__vectors[j], self.__vectors[i]
    
    def get_li_vectors(self) -> 'Matrix':
        """Returns a Matrix of Linearly Independent Vectors in this Matrix"""

        rref = self.RREF()

        # Find the vectors with only one 1 in it
        li_vectors = []
        for v in range(len(rref.vectors)):
            vector = rref.vectors[v]
            count_ones = 0
            for scalar in vector:
                if scalar not in [0, 1]:
                    count_ones = -1
                    break
                elif scalar == 1:
                    count_ones += 1
                    if count_ones > 1:
                        break
            if count_ones == 1:
                li_vectors.append(v)
        return li_vectors

    def get_ld_vectors(self) -> 'Matrix':
        """Returns a Matrix of Linearly Dependent Vectors in this Matrix"""
        li_vectors = self.get_li_vectors()
        return [ v for v in range(len(self.vectors)) if v not in li_vectors ]
    
    def rank(self) -> int:
        """Retrieves the rank of this Matrix"""
        rref = self.RREF().transpose()
        count_non_zero = 0
        for vector in rref:
            if not vector.is_zero_vector():
                count_non_zero += 1
        return count_non_zero
    
    def nullity(self) -> int:
        """Retrieves the nullity of this Matrix"""
        return self.width - self.rank()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def REF(self) -> 'Matrix':
        """A shorthand version of the row_echelon_form method"""
        return self.row_echelon_form()

    def RREF(self) -> 'Matrix':
        """A shorthand version of the reduced_row_echelon_form method"""
        return self.reduced_row_echelon_form()

    def row_echelon_form(self) -> 'Matrix':
        """Generates the Row Echelon Form of this Matrix"""

        # Start off with the first vector divided by itself to get 1
        #   We must transpose the matrix in order to modify the proper vectors
        transposed = self.transpose()
        for i in range(len(transposed.vectors)):

            # Find the next leading one and create a new transposed vector
            for k in range(len(transposed.vectors[i])):
                if transposed.vectors[i][k] != 0:
                    break
            transposed.vectors[
                i] = transposed.vectors[i] / transposed.vectors[i][k]
            for j in range(i + 1, len(transposed.vectors)):

                # Add the negated vector
                transposed.vectors[j] = transposed.vectors[j] + (
                    transposed.vectors[i] * -transposed.vectors[j][k])
        return transposed.transpose()

    def reduced_row_echelon_form(self) -> 'Matrix':
        """Generates the Reduced Row Echelon Form of this Matrix"""

        # Start off with the first vector divided by itself to get 1
        #   We must transpose the matrix in order to modify the proper vectors
        transposed = self.REF().transpose()
        for i in range(len(transposed.vectors) - 1, -1, -1):

            # Find the next leading one and create a new transposed vector
            for k in range(len(transposed.vectors[i])):
                if transposed.vectors[i][k] != 0:
                    break
            transposed.vectors[
                i] = transposed.vectors[i] / transposed.vectors[i][k]
            for j in range(i - 1, -1, -1):

                # Add the negated vector
                transposed.vectors[j] = transposed.vectors[j] + (
                    transposed.vectors[i] * -transposed.vectors[j][k])
    
        # Now order the rows correctly to get the correct RREF
        #   Find the leading ones of each vector to order it properly
        try:
            for i in range(len(transposed.vectors)):
                for j in range(len(transposed.vectors[i])):
                    if abs(transposed.vectors[i][j].numer) == abs(transposed.vectors[i][j].denom) == 1:
                        transposed.swap_vectors(i, j)
        except IndexError:
            pass
            
        return transposed.transpose()
    
    def adjugate(self) -> 'Matrix':
        """Calculates the adjugate of this Matrix"""
        pass
    
    def determinant(self) -> 'Scalar':
        """Calculates the determinant of this Matrix"""
        if self.is_square() and self.width == 1:
            return self.vectors[0][0]
        return Matrix.__determinant(self)

    def inverse(self) -> 'Matrix':
        """Generates the Inverse of this Matrix

        If an inverse cannot be done (the matrix is singular),
        None will be returned
        """

        # Only generate the inverse if the Matrix is square
        if self.is_square():
            extended = self.extend(Matrix.identity(self.width)).RREF()
            trimmed = extended.trim(self.width, start = True)
            if trimmed != Matrix.identity(self.width):
                return None
            return extended.trim(self.width)
        raise NonsquareMatrixError()
    
    def trace(self) -> 'Scalar':
        """Returns the trace of a Matrix which comes from adding up the
        diagonal of the Matrix from top-left to bottom-right
        """
        if self.is_square():
            return sum([ self[i][i] for i in range(len(self)) ])
        raise NonsquareMatrixError()

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def nullspace(self) -> 'Matrix':
        """Returns the nullspace of this Matrix"""
        rref = Matrix([
            vector for vector in self.RREF().transpose()
            if not vector.is_zero_vector()
        ]).transpose()
        linearly_independent_vectors = self.get_li_vectors()
        linearly_dependent_vectors = self.get_ld_vectors()

        # Horizontally order the vectors by the leading 1's after transposing and
        #   adding another vector for the free variables (linear dependent vectors)
        rrefT_extend = rref.transpose().extend(matrix = Matrix([
            Vector([
                0 if x != y else -1
                for y in range(rref.width)
            ])
            for x in linearly_dependent_vectors
        ]))
        for i in range(len(linearly_independent_vectors)):
            rrefT_extend.swap_vectors(i, linearly_independent_vectors[i])
        rref = rrefT_extend.transpose()
        return -Matrix([
            rref[i] for i in range(len(rref))
            if i not in linearly_independent_vectors
        ])

    def rowspace(self) -> 'Matrix':
        """Returns the rowspace of this Matrix"""
        transposed = self.RREF().transpose()

        # Find only the vectors that aren't all 0
        vectors = []
        for v in range(len(transposed.vectors)):
            found = False
            for scalar in transposed.vectors[v]:
                if scalar != 0:
                    found = True
                    break
            if found:
                vectors.append(v)
        return Matrix([
            transposed.vectors[i] 
            for i in vectors
        ])

    def columnspace(self) -> 'Matrix':
        """Returns the columnspace of this Matrix"""
        return Matrix([self[i] for i in self.get_li_vectors()])
    
    def get_orthogonal_base(self) -> 'Matrix':
        """Returns the orthogonal base of this Matrix"""

        # Keep track of each vector's orthogonality
        orthogonal = []
        for i in range(len(self)):
            base_vector = self[i]
            for j in range(len(orthogonal)):
                sub_vector = orthogonal[j]
                scalar = Scalar(
                    sub_vector * base_vector if sub_vector * sub_vector != 0 else 0,
                    sub_vector * sub_vector if sub_vector * sub_vector != 0 else 1
                )
                base_vector -= (sub_vector * scalar)
                base_vector = base_vector.factor()
            orthogonal.append(base_vector)
        
        return Matrix(orthogonal)
