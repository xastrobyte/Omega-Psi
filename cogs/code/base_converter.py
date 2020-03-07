from math import pow

BASES = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def base_to_ten(value : str, base):
    """Converts a given value from the specified base into decimal.

    Parameters
    ----------
        value: str or int
            A number in the specified base to convert to decimal
        base: int
            The base of the specified value

    Returns
    -------
        int
            The decimal equivalent of the specified value
    """

    # Validate that the number is a valid number in the specified base
    value = str(value)
    for char in value:
        if BASES.find(char) >= base:
            return None
    
    # Check if the base is 10, return the number
    if base == 10:
        return int(value)
    
    # Convert the left side of the number
    #   and add the total
    total = 0
    length = len(value)
    for char in range(length):
        digit = length - char - 1
        number = BASES.find(value[char])
        total += number * int(pow(base, digit))
    
    return total

def ten_to_base(value : int, base):
    """Converts a given decimal value into the specified base.

    Parameters
    ----------
        value : int
            A decimal number to convert
        base : int
            The target base
    
    Returns
    -------
        str
            The converted value in the specified base
    """

    # Check if the base is 10, return the value
    if base == 10:
        return value
    
    # Keep track of the remainders, which will be the new digits in the specified base
    remainders = []

    # Divide the value by the base until the number is 0
    while value != 0:
        remainders.append(value % base)
        value //= base

    # Reverse the order of the remainders and turn each digit
    #   into the proper value from the BASES string
    remainders.reverse()
    for i in range(len(remainders)):
        remainders[i] = BASES[remainders[i]]
    return "".join(remainders)

def convert(value, start, end):
    """Converts a number from a start base to its equivalent in the end base.

    Parameters
    ----------
    value : int or str
        The number to convert from a given start base to a given end base
    start : int
        The base to convert the number from
    end : int  
        The base to convert the number to

    Returns
    -------
    str
        The converted number
    """
    
    # Convert value from base_to_ten
    #   if the start value was invalid, return None
    btt = base_to_ten(value, start)
    if not btt:
        return None
    
    # Convert btt from ten_to_base
    return ten_to_base(btt, end)