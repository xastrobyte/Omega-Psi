def set_default(default_dict, result_dict):
    """Sets default values for a dictionary recursively.

    :param default_dict: The template dictionary to use to set values
    :param result_dict: The dictionary to load the template values into
    
    :rtype: dict
    """

    # Iterate through default values
    for tag in default_dict:

        # If the tag does not exist in the result dictionary, add it
        if tag not in result_dict:
            result_dict[tag] = default_dict[tag]
        
        # Tag exists in guild dict, see if tag is a dictionary
        else:
            if type(result_dict[tag]) == dict:
                result_dict[tag] = set_default(default_dict[tag], result_dict[tag])
    
    return result_dict