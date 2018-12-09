def unitFy(valuesDict):
    """Adds the units to values given in a dictionary.
    """

    # Position Values
    position = ["X", "Xo", "Xf", "Y", "Yo", "Yf"]

    # Velocity Values
    velocity = ["Vo", "Vf", "Vox", "Vfx", "Voy", "Vfy", "velocity"]

    # Acceleration Values
    acceleration = ["a"]

    # Time values
    time = ["t"]

    # Angle Values
    angle = ["theta"]

    # Setup result dict
    result = {}
    for key in valuesDict:

        # See if the value is a dict; use recursion
        if type(valuesDict[key]) == dict:
            result[key] = unitFy(valuesDict[key])
        
        # Value is not a dict; add to result
        else:
            value = valuesDict[key]

            # Add the units if value is not None
            if value != None:

                value = str(valuesDict[key])

                if key in position:
                    value += " m"
                elif key in velocity:
                    value += " m/s"
                elif key in acceleration:
                    value += " m/s^2"
                elif key in time:
                    value += " s"
                elif key in angle:
                    value += " °"
            
            result[key] = value
    
    return result