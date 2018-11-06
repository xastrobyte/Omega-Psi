from util.file.omegaPsi import OmegaPsi
from util.file.server import Server
from util.utils import sendMessage, getErrorMessage, run, timeout

from sympy.abc import x
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_parser import standard_transformations
from sympy.parsing.sympy_parser import implicit_multiplication_application

from supercog import Category, Command
import discord, sympy

class Math(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    DESCRIPTION = "Need help with math? These commands got your back."

    EMBED_COLOR = 0xFF8000

    APPENDAGES = {
        "0": "th",
        "1": "st",
        "2": "nd",
        "3": "rd",
        "4": "th",
        "5": "th",
        "6": "th",
        "7": "th",
        "8": "th",
        "9": "th"
    }

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    NO_VARIABLES = "NO_VARIABLES"

    INVALID_INPUT = "INVALID_INPUT"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(client, "Math")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._simplify = Command(commandDict = {
            "alternatives": ["simplify", "simp", "evaluate", "eval"],
            "info": "Simplifies a mathematical expression.",
            "parameters": {
                "expression": {
                    "info": "The expression to simplify.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To simplify an expression, you need an expression."
                    ]
                }
            }
        })

        self._expand = Command(commandDict = {
            "alternatives": ["expand", "exp", "e"],
            "info": "Expands a mathematical expression.",
            "parameters": {
                "expression": {
                    "info": "The expression to expand.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To expand an expression, you need an expression."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "To expand an expression, you need only 1 expression."
                    ]
                }
            }
        })

        self._factor = Command(commandDict = {
            "alternatives": ["factor", "f"],
            "info": "Factors a mathematical expression.",
            "parameters": {
                "expression": {
                    "info": "The expression to factor.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To factor an expression, you need an expression."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "To factor an expression, you need only 1 expression."
                    ]
                }
            }
        })

        self._factorial = Command(commandDict = {
            "alternatives": ["factorial", "!"],
            "info": "Gets the factorial of a number.",
            "parameters": {
                "number": {
                    "info": "The number to get the factorial of.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To get the factorial of a number, you need a number."
                    ]
                },
                Math.INVALID_INPUT: {
                    "messages": [
                        "That is not a number."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "To get the factorial of a number, you need 1 number."
                    ]
                }
            }
        })

        self._fibonacci = Command(commandDict = {
            "alternatives": ["fibonacci", "fib"],
            "info": "Gets the fibonacci number of a number.",
            "parameters": {
                "number": {
                    "info": "The number to get the fibonacci number of.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To get the fibonacci number of a number, you need a number."
                    ]
                },
                Math.INVALID_INPUT: {
                    "messages": [
                        "That is not a number."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "To get the fibonacci number of a number, you need 1 number."
                    ]
                }
            }
        })

        self._solve = Command(commandDict = {
            "alternatives": ["solve", "system"],
            "info": "Solves an equation or a system of equations.",
            "parameters": {
                "equation(s)": {
                    "info": "The equation(s) to solve.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To solve an equation, or system of equations, you need the equation(s)."
                    ]
                }
            }
        })

        self._substitute = Command(commandDict = {
            "alternatives": ["substitute", "subs"],
            "info": "Substitutes variables in an equation.",
            "parameters": {
                "expression": {
                    "info": "The expression to substitute variables for.",
                    "optional": False
                },
                "variables": {
                    "info": "The variables to substitute in the expression.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to substitute variables in an expression, you need the expression and the variables."
                    ]
                },
                Math.NO_VARIABLES: {
                    "messages": [
                        "There are no variables to substitute."
                    ]
                }
            }
        })

        self._derivative = Command(commandDict = {
            "alternatives": ["derivative", "derivate", "dv"],
            "info": "Gets the derivative of an expression.",
            "parameters": {
                "expression": {
                    "info": "The expression to get the derivative of.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To get the derivative of an expression, you need an expression."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "To get the derivative of an expression, you need 1 expression."
                    ]
                }
            }
        })

        self._integral = Command(commandDict = {
            "alternatives": ["integral", "integrate"],
            "info": "Gets the integral of an expression.",
            "parameters": {
                "expression": {
                    "info": "The expression to get the integral of.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To get the integral of an expression, you need an expression."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "To get the integral of an expression, you need 1 expression."
                    ]
                }
            }
        })

        self.setCommands({
            self._simplify,
            self._expand,
            self._factor,
            self._factorial,
            self._solve,
            self._substitute,
            self._fibonacci,
            self._derivative,
            self._integral
        })

        self._transformations = (standard_transformations + (implicit_multiplication_application,))
        self._FIBONACCI = {}
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @timeout(5, "The simplify function timed out.")
    def simplify(self, expression):
        """Simplifies an expression using sympy.\n

        expression - The expression to simplify.\n
        """
        
        # Standardize expression
        originalExpression = expression
        expression = expression.replace(" ", "")
        try:
            result = str(eval(expression))
        except:
            expression = self._standardize(expression)
            result = str(sympy.simplify(expression)).replace("**", "^").replace("*", "")

        # Return the result in an embed
        return discord.Embed(
            title = "Evaluation of `{}`".format(originalExpression),
            description = result,
            colour = Math.EMBED_COLOR
        )
    
    @timeout(5, "The expand function timed out.")
    def expand(self, expression):
        """Expands an expression using sympy.\n

        expression - The expression to expand.\n
        """

        # Standardize expression
        originalExpression = expression
        expression = self._standardize(expression)

        # Return the result in an embed
        return discord.Embed(
            title = "Expansion of `{}`".format(originalExpression),
            description = str(sympy.simplify(expression)).replace("**", "^").replace("*", ""),
            colour = Math.EMBED_COLOR
        )
    
    @timeout(5, "The factor function timed out.")
    def factor(self, expression):
        """Factors an expression using sympy.\n

        expression - The expression to factor.\n
        """
        
        # Standardize expression
        originalExpression = expression
        expression = self._standardize(expression)

        # Return the result in an embed
        return discord.Embed(
            title = "Factoring of `{}`".format(originalExpression),
            description = str(sympy.factor(expression)).replace("**", "^").replace("*", ""),
            colour = Math.EMBED_COLOR
        )
    
    @timeout(5, "The factorial function timed out.")
    def factorial(self, number):
        """Gets the factorial of a number.\n

        number - The number to get the factorial of.\n
        """
        
        # Loop through number
        originalNumber = number
        try:
            number = int(number)
        except:
            return getErrorMessage(self._factorial, Math.INVALID_INPUT)

        for n in range(number - 1, 0, -1):
            number *= n

        # Setup embed
        embed = discord.Embed(
            title = "Factorial of `{}`".format(originalNumber),
            description = " ",
            colour = Math.EMBED_COLOR
        )

        # Turn number into string and split into fields
        number = str(number)
        fieldText = ""
        fields = []

        # Add characters to field text and add embed to field if necessary
        for char in number:
            if len(fieldText) + 1 >= OmegaPsi.MESSAGE_THRESHOLD:
                fields.append(fieldText)
                fieldText = ""
            
            fieldText += char
        
        if len(fieldText) > 0:
            fields.append(fieldText)
        
        fieldCount = 0
        for field in fields:
            fieldCount += 1
            embed.add_field(
                name = "Result {}".format(
                    "({} / {})".format(
                        fieldCount, len(fields)
                    ) if len(fields) > 1 else ""
                ),
                value = field,
                inline = False
            )

        # Return the result in an embed
        return embed
    
    @timeout(5, "The solve function timed out.")
    def solve(self, expressions):
        """Solves an expression, or expressions, using sympy.\n

        expressions - The expressions to solve.\n
        """
        
        # Standardize each expression
        originalExpression = "\n".join(expressions)
        for exp in range(len(expressions)):

            # Check if expression has "="
            eqIndex = expressions[exp].find("=")
            if eqIndex != -1:

                # Get left and right sides
                left = expressions[exp][:eqIndex]
                right = expressions[exp][eqIndex + 1:]
                expressions[exp] = left + "- ({})".format(right)
            
            expressions[exp] = self._standardize(expressions[exp])
        
        # Get variables and values; Add to String
        varDict = sympy.solve(expressions)
        result = ""
        for variable in varDict:
            result += "{} = {}\n".format(
                variable, varDict[variable]
            )
        
        return discord.Embed(
            title = "Solution",
            description = "`{}`\n".format(originalExpression) + result,
            colour = Math.EMBED_COLOR
        )
    
    @timeout(5, "The substitute function timed out.")
    def substitute(self, expression, variables):
        """Substitutes an expression with variables using sympy.\n

        expression - The expression to substitute.\n
        variables - The variables to substitute in the expression.\n
        """
        
        # Turn variables into a variable dictionary
        originalExpression = expression
        varDict = {}
        for variable in variables:

            # Find "=", variable, and value
            equals = variable.find("=")
            var = variable[:equals]
            value = variable[equals + 1:]
            varDict[var] = value
        
        variables = varDict
        if len(variables) == 0:
            return getErrorMessage(self._substitute, Math.NO_VARIABLES)
        
        # Standardize expression
        expression = self._standardize(expression)

        return discord.Embed(
            title = "Subsitution of `{}`".format(originalExpression),
            description = str(eval(str(expression.subs(variables)))),
            colour = Math.EMBED_COLOR
        )
    
    @timeout(5, "The fibonacci function timed out.")
    def fibonacci(self, number):
        """Gets the fibonacci of a number.\n

        number - The number to get the fibonacci of.\n
        """

        return discord.Embed(
            title = "`{}{}` Fibonacci number".format(
                number,
                Math.APPENDAGES[str(number)[-1]]
            ),
            description = str(self._fibonacciHelper(number)),
            colour = Math.EMBED_COLOR
        )
    
    def _fibonacciHelper(self, number):
        """Gets the fibonacci of a number.\n

        number - The number to get the fibonacci of.\n
        """

        # Check if number is less than 2
        try:
            number = int(number)
        except:
            return getErrorMessage(self._fibonacci, Math.INVALID_INPUT)
            
        if number < 2:
            return number
        
        # Check if number's value is known
        if str(number) in self._FIBONACCI:
            return self._FIBONACCI[str(number)]
        
        # Get fib of number and save it in fibonacci numbers
        else:
            self._FIBONACCI[str(number)] = self._fibonacciHelper(number - 2) + self._fibonacciHelper(number - 1)
            return self._FIBONACCI[str(number)]
    
    @timeout(5, "The derivative function timed out.")
    def derivative(self, expression):
        """Gets the derivative of an expression using sympy.\n

        expression - The expression to get the derivative of.\n
        """
        
        # Standardize expression
        originalExpression = expression
        expression = self._standardize(expression)

        return discord.Embed(
            title = "Derivative of `{}`".format(originalExpression),
            description = str(sympy.diff(expression)).replace("**", "^").replace("*", ""),
            colour = Math.EMBED_COLOR
        )
    
    @timeout(5, "The integral function timed out.")
    def integral(self, expression):
        """Gets the integral of an expression using sympy.\n

        expression - The expression to get the integral of.\n
        """
        
        # Standardize expression
        originalExpression = expression
        expression = self._standardize(expression)

        return discord.Embed(
            title = "Integral of `{}`".format(originalExpression),
            description = str(sympy.integrate(expression, x)).replace("**", "^").replace("*", ""),
            colour = Math.EMBED_COLOR
        )

    def _standardize(self, expression):
        """Standardizes the expression so sympy can read it.\n

        expression - The expression to standardize.\n
        """

        # Standardize expressions using parse_expr
        return parse_expr(expression.replace("^", "**"), transformations = self._transformations)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs an Math Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Simplify Command
            if command in self._simplify.getAlternatives():

                # 0 Parameters Exist (NOT_ENOUGH_PARAMETERS)
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._simplify, Category.NOT_ENOUGH_PARAMETERS)
                    )

                # 1 or More Parameter Exists (simplify)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._simplify, self.simplify, " ".join(parameters))
                    )
            
            # Expand Command
            elif command in self._expand.getAlternatives():

                # 0 Parameters Exist (NOT_ENOUGH_PARAMETERS)
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._expand, Category.NOT_ENOUGH_PARAMETERS)
                    )

                # 1 Parameter Exists (expand)
                elif len(parameters) == 1:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._expand, self.expand, parameters[0])
                    )

                # 2 or More Parameters Exist (TOO_MANY_PARAMETERS)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._expand, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Factor Command
            elif command in self._factor.getAlternatives():

                # 0 Parameters Exist (NOT_ENOUGH_PARAMETERS)
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._factor, Category.NOT_ENOUGH_PARAMETERS)
                    )

                # 1 Parameter Exists (factor)
                elif len(parameters) == 1:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._factor, self.factor, parameters[0])
                    )

                # 2 or More Parameters Exist (TOO_MANY_PARAMETERS)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._factor, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Factorial Command
            elif command in self._factorial.getAlternatives():

                # 0 Parameters Exist (NOT_ENOUGH_PARAMETERS)
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._factorial, Category.NOT_ENOUGH_PARAMETERS)
                    )

                # 1 Parameter Exists (factorial)
                elif len(parameters) == 1:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._factorial, self.factorial, parameters[0])
                    )

                # 2 or More Parameters Exist (TOO_MANY_PARAMETERS)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._factorial, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Solve Command
            elif command in self._solve.getAlternatives():

                # 0 Parameters Exist (NOT_ENOUGH_PARAMETERS)
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._solve, Category.NOT_ENOUGH_PARAMETERS)
                    )

                # 1 or More Parameter Exists (solve)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._solve, self.solve, parameters)
                    )
            
            # Substitute Command
            elif command in self._substitute.getAlternatives():

                # Less than 2 Parameters Exist (NOT_ENOUGH_PARAMETERS)
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._substitute, Category.NOT_ENOUGH_PARAMETERS)
                    )

                # 2 or More Parameter Exists (substitute)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._substitute, self.substitute, parameters[0], parameters[1:])
                    )
            
            # Fibonacci Command
            elif command in self._fibonacci.getAlternatives():

                # 0 Parameters Exist (NOT_ENOUGH_PARAMETERS)
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._fibonacci, Category.NOT_ENOUGH_PARAMETERS)
                    )

                # 1 Parameter Exists (fibonacci)
                elif len(parameters) == 1:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._fibonacci, self.fibonacci, parameters[0])
                    )

                # 2 or More Parameters Exist (TOO_MANY_PARAMETERS)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._fibonacci, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Derivative Command
            elif command in self._simplify.getAlternatives():

                # 0 Parameters Exist (NOT_ENOUGH_PARAMETERS)
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._derivative, Category.NOT_ENOUGH_PARAMETERS)
                    )

                # 1 Parameter Exists (derivative)
                elif len(parameters) == 1:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._derivative, self.derivative, parameters[0])
                    )

                # 2 or More Parameters Exist (TOO_MANY_PARAMETERS)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._derivative, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Integral Command
            elif command in self._integral.getAlternatives():

                # 0 Parameters Exist (NOT_ENOUGH_PARAMETERS)
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._integral, Category.NOT_ENOUGH_PARAMETERS)
                    )

                # 1 Parameter Exists (integral)
                elif len(parameters) == 1:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._integral, self.integral, parameters[0])
                    )

                # 2 or More Parameters Exist (TOO_MANY_PARAMETERS)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._integral, Category.TOO_MANY_PARAMETERS)
                    )

def setup(client):
    client.add_cog(Math(client))
