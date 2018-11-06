import math

BASES = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"

def numberToTen(number, startBase):
    """Converts a number from a different base to Base-10.\n

    - number - The number to convert.\n
    - startBase - The base the number is in.\n
    """

    # Make sure number is a number in the startBase
    number = str(number)
    for char in number:
        if BASES.find(char) >= startBase:
            return None

    # Setup total number
    total = 0

    # Iterate through number as string
    length = len(number)
    for char in range(length):
        
        # Get digit
        digit = length - char - 1
        
        # Get digit's value
        value = BASES.find(number[char])
        
        # Add value multiplied by base to total
        total += value * int(math.pow(startBase, digit))

    return total

def tenToNumber(number, endBase):
    """Converts a number from Base-10 to another base.\n

     - number - The number to convert from Base-10.\n
     - endBase - The base to convert to.\n
    """

    # Make sure number is a base10 number
    try:
        number = int(number)
    except:
        return None

    # Get maximum power of result using math.ln
    power = int(math.log10(number) / math.log10(endBase))
    
    # Setup converted value
    final = ""

    # Do loop until number / endBase is zero
    while True:

        # Check if number < endBase
        # Add number conversion to final; Break
        if number < endBase:
            final += BASES[number]
            break

        # Divide number by endBase
        digit = int(number / int(math.pow(endBase, power)))

        # Add digit to final
        final += BASES[digit]

        # Subtract (digit * endBase ^ power) from number
        number -= (digit * int(math.pow(endBase, power)))

        # Reduce power by 1
        power -= 1

    return final

def convert(number, startBase, endBase):
    """Converts a number from the startBase to the endBase.\n

     - startBase - The base to start at.\n
     - endBase - The base to end with.\n
    """

    # Get number to base10
    base10 = numberToTen(number, startBase)

    # Get base10 to number
    return tenToNumber(base10, endBase) 
