MEMORY_SIZE = 2 ** 15
VALID_CHARS = "><+-.[]"

# # # # # # # # # # # # # # #

memory = [0] * MEMORY_SIZE

# # # # # # # # # # # # # # #

def debug_bf(pointer):
    """Debugs brainfuck code based off the current index

    :param code: The brainfuck code to debug
    :param pointer: The current pointer of memory
    """

    # Create the carat string which points to the current memory cell
    longest_value = 0
    for cell in memory:
        if len(str(cell)) > len(str(longest_value)):
            longest_value = cell

    # Center each cell index
    memory_cells = " ".join([
        str(i).center(len(str(longest_value)))
        for i in range(len(memory))
    ])

    # Center each cell's value
    value_cells = " ".join([
        str(value).center(len(str(longest_value)))
        for value in memory
    ])

    # Center each carat
    carat_cells = " ".join([
        "^".center(len(str(longest_value)))
        if i == pointer else " ".center(len(str(longest_value)))
        for i in range(len(memory))
    ])

    return f"{memory_cells}\n{value_cells}\n{carat_cells}"
    

def compile_bf(code):
    """Compiles modified Brainfuck code
    which doesn't allow for input

    :param code: The brainfuck code to compile
    """

    # Check if debugging is active
    code = code.strip()
    debug = False
    if code[0] == "#":
        code = code[1:]
        debug = True

    # Remove all invalid characters
    code = "".join([
        char for char in code 
        if char in VALID_CHARS
    ])

    # Compile the program
    pointer = 0
    output = ""
    i = 0
    loop = []

    # When compiling, keep track of the previous bracket
    #   for looping
    prev_bracket = -1
    while i < len(code):
        if debug:
            print(debug_bf(pointer))
        char = code[i]

        # Move the memory pointer right or left
        if char == ">":
            pointer += 1
            if pointer >= len(memory):
                memory.append(0)
        elif char == "<":
            pointer -= 1
        
        # Increment or decrement the current cell
        elif char == "+":
            memory[pointer] += 1
            if memory[pointer] > 255:
                memory[pointer] = 0
        elif char == "-":
            memory[pointer] -= 1
            if memory[pointer] < 0:
                memory[pointer] = 255
        
        # Output text
        elif char == ".":
            if memory[pointer] < 32:
                output += "□"
            else:
                output += chr(memory[pointer])
        
        # Loop until the current memory cell is 0
        elif char == "[":
            loop.append(i)
        elif char == "]":
            if memory[pointer] != 0:
                i = loop[-1]
            else:
                loop = loop[:-1]

        # Move to the next character
        i += 1
    
    return output
