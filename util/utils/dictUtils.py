def setDefault(defaultDict, resultDict):
    """Sets the default values in a dictionary recursively.

    Parameters:
        defaultDict (dict): The dictionary that holds the default values.
        resultDict (dict): The dictionary to set the default values in.
    """

    # Iterate through default values
    for tag in defaultDict:

        # If the tag does not exist in the result dictionary, add it
        if tag not in resultDict:
            resultDict[tag] = defaultDict[tag]
        
        # The tag exists in the result dictionary, see if the value is a dictionary
        # If the value is a dictionary, set any default values in there too.
        else:
            if type(resultDict[tag]) == dict:
                resultDict[tag] = setDefault(defaultDict[tag], resultDict[tag])

    return resultDict

def removeUnused(defaultDict, resultDict):
    """Removes unused values from a dictionary recursively.

    Parameters:
        defaultDict (dict): The dictionary that holds the default values.
        resultDict (dict): The dictionary to remove the default values from.
    """
    
    # Keep track of unused tags
    unused = []

    # Iterate through the result dictionary
    for tag in resultDict:

        # If the tag does not exist in the default dictionary, remove it
        if tag not in defaultDict:
            unused.append(tag)
        
        # The tag exists in the default dictionary, see if the value is a dictionary
        # If the value is a dictionary, remove any values that are unused
        else:
            if type(resultDict[tag]) == dict:
                resultDict[tag] = removeUnused(defaultDict[tag], resultDict[tag])

    # Remove all unused tags
    for tag in unused:
        resultDict.pop(tag)

    return resultDict