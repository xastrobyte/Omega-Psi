from math import gcd
from typing import Union, TYPE_CHECKING

from .errors import NotAnIntegerError

if TYPE_CHECKING:
    from .matrix import Matrix

class Scalar:
    """A value to be inserted into a Matrix or a Vector

    By specifying only `numer` this Scalar acts as an integer
    The default Scalar is 0

    :param numer: The numerator of the Scalar
    :param denom: The denominator of the Scalar
    """

    @staticmethod
    def simplify_fraction(numer: int, denom: int):
        """Simplifies a fraction to the simplest form.
        If there is a negative in the denominator, it will be moved to the numerator

        :param numer: The numerator of the fraction
        :param denom: The denominator of the fraction

        :raises ZeroDivisionError: When the denominator given is 0
        """

        # Check if the denominator is 0 (invalid)
        if denom == 0:
            raise ZeroDivisionError()

        # Simplify the fraction by first checking if the numerator
        #   is the same as the denominator
        if numer == denom:
            return 1, 1

        # Use math.gcd to find the GCD of numer and denom
        divide_by = gcd(numer, denom)
        numer //= divide_by
        denom //= divide_by

        # Swap the negative from the denom to numer if necessary
        if denom < 0:
            numer *= -1
            denom *= -1

        return numer, denom

    def __init__(self, numer: Union['Scalar', int]=0, denom: Union['Scalar', int]=1):

        # Check if either one of numer or denom is text and not an integer
        try:
            if not isinstance(numer, Scalar):
                numer = int(numer)
            if not isinstance(denom, Scalar):
                denom = int(denom)
        except ValueError:
            raise NotAnIntegerError()

        # Check if both the numerator and denominator are Scalars
        if isinstance(numer, Scalar) and isinstance(denom, Scalar):
            numer, denom = numer.numer * denom.denom, numer.denom * denom.numer

        # The numerator is a Scalar but the denominator is an int
        elif isinstance(numer, Scalar):
            numer, denom = numer.numer, numer.denom * denom

        # The numerator is an int but the denominator is a Scalar
        elif isinstance(denom, Scalar):
            numer, denom = numer * denom.denom, denom.numer

        self.__numer, self.__denom = Scalar.simplify_fraction(numer, denom)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __str__(self) -> str:
        if self.denom == 1 or self.numer == 0:
            return f"{self.numer}"
        return f"{self.numer}/{self.denom}"

    def __neg__(self) -> 'Scalar':
        return Scalar(-self.numer, self.denom)

    def __eq__(self, scalar: Union['Scalar', int]) -> bool:
        if isinstance(scalar, int):
            scalar = Scalar(scalar)
        return self.numer == scalar.numer and self.denom == scalar.denom
    
    def __req__(self, scalar: Union['Scalar', int]) -> bool:
        return self == scalar
    
    def __gt__(self, value: Union['Scalar', int]) -> bool:
        if isinstance(value, int):
            return (self.numer // self.denom) > value
        return (self.numer * value.denom) > (value.numer * self.denom)
    
    def __ge__(self, value: Union['Scalar', int]) -> bool:
        return self > value or self == value
    
    def __lt__(self, value: Union['Scalar', int]) -> bool:
        return not (self > value)
    
    def __le__(self, value: Union['Scalar', int]) -> bool:
        return not (self > value) or self == value

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __mul__(self, value: Union['Matrix', 'Scalar', int]) -> ['Matrix', 'Scalar']:
        """Multiplies two values together using the form
        (x1 * x2) / (y1 * y2)
        """

        # Check if the given value is a Matrix
        if isinstance(value, type('Matrix')):
            return self * value

        # Check if the given value is a scalar or a fraction
        x1, y1 = self.numer, self.denom
        if isinstance(value, int):
            x2, y2 = value, 1
        else:
            x2, y2 = value.numer, value.denom

        # Check if the resulting fraction is equal to 1
        # if (abs(x1 * x2) == abs(y1 * y2) or 
        #     abs(y1 * y2) == 1 or 
        #     abs(x1 * x2) == 0):
        #     return (x1 * x2) // (y1 * y2)
        return Scalar(x1 * x2, y1 * y2)

    def __rmul__(self, value: Union['Matrix', 'Scalar', int]) -> ['Matrix', 'Scalar']:
        """Multiplies two values together using the form
        (x1 * x2) / (y1 * y2)
        """
        return self * value

    def __truediv__(self, value: Union['Scalar', int]) -> 'Scalar':
        """Multiplies two values together using the form
        (x1 * y2) / (y1 * x2)
        """

        # Check if the given value is a scalar or a fraction
        x1, y1 = self.numer, self.denom
        if isinstance(value, int):
            x2, y2 = value, 1
        else:
            x2, y2 = value.numer, value.denom

        # Check if the resulting fraction is equal to 1
        # if (abs(x1 * y2) == abs(y1 * x2) or 
        #     abs(y1 * x2) == 1 or
        #     abs(x1 * y2) == 0):
        #     return (x1 * y2) // (y1 * x2)
        return Scalar(
            x1 * y2 if (y1 * x2) != 0 else 0, 
            y1 * x2 if (y1 * x2) != 0 else 1
        )

    def __add__(self, value: Union['Scalar', int]) -> 'Scalar':
        """Adds two values together using the form
        ((y2 * x1) / (y2 * y1)) + ((x2 * y1) / (y2 * y1))
        """

        # Check if the given value is a scalar or a fraction
        x1, y1 = self.numer, self.denom
        if isinstance(value, int):
            x2, y2 = value, 1
        else:
            x2, y2 = value.numer, value.denom

        # Check if the resulting fraction is equal to 1
        # if (abs((y2 * x1) + (x2 * y1)) == abs(y2 * y1) or 
        #     abs(y2 * y1) == 1 or
        #     abs((y2 * x1) + (x2 * y1)) == 0):
        #     return ((y2 * x1) + (x2 * y1)) // (y2 * y1)
        return Scalar(
            (y2 * x1) + (x2 * y1),
            y2 * y1
        )

    def __radd__(self, value: Union['Scalar', int]) -> 'Scalar':
        """Adds two values together using the form
        ((y2 * x1) / (y2 * y1)) + ((x2 * y1) / (y2 * y1))
        """
        return self.__add__(value)

    def __sub__(self, value: Union['Scalar', int]) -> 'Scalar':
        """Subtracts two values together using the form
        ((y2 * x1) / (y2 * y1)) - ((x2 * y1) / (y2 * y1))
        """

        # Check if the given value is a scalar or a fraction
        x1, y1 = self.numer, self.denom
        if isinstance(value, int):
            x2, y2 = value, 1
        else:
            x2, y2 = value.numer, value.denom

        # Check if the resulting fraction is equal to 1
        # if (abs((y2 * x1) - (x2 * y1)) == abs(y2 * y1) or 
        #     abs(y2 * y1) == 1 or
        #     abs((y2 * x1) - (x2 * y1)) == 0):
        #     return ((y2 * x1) - (x2 * y1)) // (y2 * y1)
        return Scalar(
            (y2 * x1) - (x2 * y1),
            y2 * y1
        )

    def __rsub__(self, value: Union['Scalar', int]) -> 'Scalar':
        """Subtracts two values together using the form
        ((y2 * x1) / (y2 * y1)) - ((x2 * y1) / (y2 * y1))
        """
        return self - value

    def __pow__(self, n: int) -> 'Scalar':
        """Returns this Scalar raised to the n-th power

        :param n: The power to raise this Scalar to
        """
        return Scalar(
            self.numer ** n,
            self.denom ** n
        )

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def numer(self) -> int:
        return self.__numer
    
    @property
    def denom(self) -> int:
        return self.__denom