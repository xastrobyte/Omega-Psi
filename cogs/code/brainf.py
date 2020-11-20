MEMORY_SIZE = 8192
VALID_CHARS = "><+-.[]"

# # # # # # # # # # # # # # #

memory = [0] * MEMORY_SIZE

# # # # # # # # # # # # # # #

def compile_bf(code):
    """Compiles modified Brainfuck code with parameters, if specified

    :param code: The brainfuck code to compile
    """

    # Remove all invalid characters
    code = "".join([
        char for char in code 
        if char in VALID_CHARS
    ])

    # Compile the program
    pointer = 0
    output = ""
    i = 0
    while i < len(code):
        char = code[i]

        # Move the memory pointer right or left
        if char == ">":
            pointer += 1
        elif char == "<":
            pointer -= 1
        
        # Increment or decrement the current cell
        elif char == "+":
            memory[pointer] += 1
        elif char == "-":
            memory[pointer] -= 1
        
        # Output text
        elif char == ".":
            out_char = chr(memory[pointer])
            if out_char.isprintable():
                output += out_char
            else:
                output += "□"
        
        # Loop until the current memory cell is 0
        elif char == "[":
            # TODO: Implement looping
            pass
        elif char == "]":
            # TODO: Implement looping
            pass
    
    return output