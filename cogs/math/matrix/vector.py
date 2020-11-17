from math import gcd
from typing import Union

from .errors import SizeMismatchError, OrientationMismatchError
from .scalar import Scalar

class Vector:
    """A Vector holds an array of values either vertically or horizontally
    By default, Vectors are vertical and are immutable.

    :param vector: The vector contents
    :param transposed: Whether or not to transpose the vector once stored
    """

    def __init__(self, scalars: list, *, transposed = False):
        vector_tuple = []
        for x in scalars:
            if isinstance(x, int):
                x = Scalar(x)
            vector_tuple.append(x)
        self.__vector_tuple = tuple(vector_tuple)
        self.__size = len(scalars)
        self.__transposed = transposed
    
    # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def __str__(self) -> str:

        # Check if the Vector is horizontal/transposed
        if self.is_transposed():
            return "[ {} ]".format(" ".join([
                str(scalar)
                for scalar in self.__vector_tuple
            ]))
        
        # Find the longest length number to center all numbers in the vector
        length = 0
        for v in self.__vector_tuple:
            if len(str(v)) > length:
                length = len(str(v))

        return "\n".join([ f"| {str(v).center(length)} |" for v in self.__vector_tuple ])
    
    def __eq__(self, vector: 'Vector') -> bool:
        if self.is_transposed() != vector.is_transposed() or len(self) != len(vector):
            return False
        for scalar in range(len(self)):
            if self[scalar] != vector[scalar]:
                return False
        return True
    
    # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def __getitem__(self, index: int) -> int:
        return self.__vector_tuple[index]

    def __len__(self) -> int:
        return len(self.__vector_tuple)
    
    # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def __mul__(self, value: Union['Vector', 'Scalar', int]) -> ['Vector', 'Scalar']:
        """Multiplies this Vector by another Vector (cross product), or by a Scalar
        (fraction or int)

        :param value: The Vector or Scalar to multiply by
        """

        # Check if the value given is a Vector (cross product)
        #   Transpose only one of the Vectors
        if isinstance(value, Vector):
            if len(value) == len(self):

                # Transpose one of the vectors if needed
                transpose_back = False
                if not (self.is_transposed() ^ value.is_transposed()):
                    self.transpose()
                    transpose_back = True
                scalar = Scalar(0)
                for x in range(len(self)):
                    scalar += (self[x] * value[x])
                if transpose_back:
                    self.transpose()  # Transpose this Vector back to it's original form
                return scalar
            else:
                raise SizeMismatchError()
        
        # The value given is a Scalar or int
        else:
            if isinstance(value, int):
                value = Scalar(value)
            return Vector([
                value * self[x]
                for x in range(len(self))
            ])
    
    def __rmul__(self, value: Union['Vector', 'Scalar', int]) -> ['Vector', 'Scalar']:
        """Multiplies this Vector by another Vector (cross product), or by a Scalar
        (fraction or int)

        :param value: The Vector or Scalar to multiply by
        """
        return self * value
    
    def __truediv__(self, value: Union['Scalar', int]) -> 'Vector':
        """Divides this Vector by a Scalar (fraction or int)

        :param value: The Scalar to divide by
        """
        if isinstance(value, int):
            value = Scalar(value)
        return Vector([
            self[x] / value
            for x in range(len(self))
        ])
    
    def __add__(self, value: 'Vector') -> 'Vector':
        """Adds two vectors together"""
        if len(self) == len(value) and self.is_transposed() == value.is_transposed():
            return Vector([ self[x] + value[x] for x in range(len(self)) ])
        raise OrientationMismatchError()
    
    def __sub__(self, value: 'Vector') -> 'Vector':
        """Adds two vectors together"""
        if len(self) == len(value) and self.is_transposed() == value.is_transposed():
            return Vector([ self[x] - value[x] for x in range(len(self)) ])
        raise OrientationMismatchError()

    # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def is_transposed(self) -> bool:
        """Returns whether or not this Vector is transposed (Horizontal)"""
        return self.__transposed
    
    def is_zero_vector(self) -> bool:
        """Returns whether or not this Vector is a Zero Vector"""
        for scalar in self:
            if scalar.numer != 0:
                return False
        return True
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def transpose(self):
        """Swaps the orientation of the Vector between horizontal
        and vertical
        """
        self.__transposed = not self.__transposed
    
    def factor(self) -> 'Vector':
        """Multiplies this Vector by the greatest common denominator
        of all the Scalars in this Vector and returns the result
        """
        lowest_gcd = self[0].denom
        for scalar in self:
            temp_gcd = abs(scalar.denom)
            if temp_gcd > lowest_gcd:
                lowest_gcd = temp_gcd
        return Vector([
            scalar * Scalar(lowest_gcd)
            for scalar in self
        ])
    
    def norm(self, p: int=2, *, raw: bool=False) -> 'Scalar':
        """Returns the p-norm of this Vector which comes from

        :param p: The p value to use (Default: 2)
        :param raw: Whether or not to return the sum of the values
            prior to doing norm ^ (1/p) (Default: False)

        || v ||p = (vT * v) ^ (1/p)
                 = (x1^p + ... + xk^p)^(1/n)
        """
        norm_value = 0
        for x in self:
            norm_value += self[x] ** p
        if raw:
            return norm_value
        return norm_value ** (1 / p)
