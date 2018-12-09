from util.file.database import loop
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server

from util.math.kinematics import Kinematics

from util.utils.discordUtils import sendMessage, getErrorMessage

from sympy.abc import x
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_parser import standard_transformations
from sympy.parsing.sympy_parser import implicit_multiplication_application

from supercog import Category, Command
import discord, sympy

scrollEmbeds = {}

class Math(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

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
        super().__init__(
            client, 
            "Math",
            description = "Need help with math? These commands got your back.",
            embed_color = 0xFF8000,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

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
            },
            "command": self.simplify
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
            },
            "command": self.expand
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
            },
            "command": self.factor
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
            },
            "command": self.factorial
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
            },
            "command": self.solve
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
            },
            "command": self.substitute
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
            },
            "command": self.derivative
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
            },
            "command": self.integral
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
            },
            "command": self.fibonacci
        })

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Physics
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self._solveKinematics = Command(commandDict = {
            "alternatives": ["solveKinematics", "solveKine", "kine", "kinematics"],
            "info": "Solves for Basic Linear Kinematic Physics. Can be used for Horizontal or Vertical motion. To clarify a variable, make sure you set the variable (Vf=5 a=9.6 etc.)",
            "parameters": {
                "X=": {
                    "info": "The displacement of an object (in meters). If this is given, Xo will be assumed to be 0 meters.",
                    "optional": True
                },
                "Xo=": {
                    "info": "The initial position of an object (in meters).",
                    "optional": True
                },
                "Xf=": {
                    "info": "The final position of an object (in meters).",
                    "optional": True
                },
                "V=": {
                    "info": "The velocity of an object (in meters / second). If this is given, Vo and Vf will be assumed to be the value of this.",
                    "optional": True
                },
                "Vo=": {
                    "info": "The initial velocity of an object (in meters / second).",
                    "optional": True
                },
                "Vf=": {
                    "info": "The final velocity of an object (in meters / second).",
                    "optional": True
                },
                "a=": {
                    "info": "The acceleration of an object (in meters / second^2)",
                    "optional": True
                },
                "t=": {
                    "info": "The time that an acceleration or velocity acts on an object (in seconds).",
                    "optional": True
                }
            },
            "errors": {
                Math.INVALID_PARAMETER: {
                    "messages": [
                        "You have an invalid variable in there somewhere."
                    ]
                },
                Math.INVALID_INPUT: {
                    "messages": [
                        "A value you gave was not a number."
                    ]
                },
                Math.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters to solve for kinematics."
                    ]
                }
            },
            "command": self.solveKinematics
        })

        self.setCommands([
            # Math Commands
            self._simplify,
            self._expand,
            self._factor,
            self._factorial,
            self._solve,
            self._substitute,
            self._derivative,
            self._integral,
            self._fibonacci,

            # Physics Commands
            self._solveKinematics
        ])

        self._transformations = (standard_transformations + (implicit_multiplication_application,))
        self._FIBONACCI = {}
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def simplify(self, message, parameters):
        """Simplifies an expression using sympy.\n

        expression - The expression to simplify.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._simplify.getMinParameters():
            embed = getErrorMessage(self._simplify, Math.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            expression = " ".join(parameters)
        
            # Standardize expression
            originalExpression = expression
            expression = expression.replace(" ", "")
            try:
                expression = self._standardize(expression)

                result = await loop.run_in_executor(None,
                    sympy.simplify,
                    expression
                )
                result = str(result).replace("**", "^").replace("*", "")
                
            except:
                result = str(eval(expression))

            embed = discord.Embed(
                title = "Evaluation of `{}`".format(originalExpression),
                description = result,
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def expand(self, message, parameters):
        """Expands an expression using sympy.\n

        expression - The expression to expand.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._expand.getMinParameters():
            embed = getErrorMessage(self._expand, Math.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            expression = " ".join(parameters)

            # Standardize expression
            originalExpression = expression
            expression = self._standardize(expression)

            result = await loop.run_in_executor(None,
                sympy.simplify,
                expression
            )
            result = str(result).replace("**", "^").replace("*", "")

            # Return the result in an embed
            embed = discord.Embed(
                title = "Expansion of `{}`".format(originalExpression),
                description = result,
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def factor(self, message, parameters):
        """Factors an expression using sympy.\n

        expression - The expression to factor.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._factor.getMinParameters():
            embed = getErrorMessage(self._factor, Math.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            expression = " ".join(parameters)
        
            # Standardize expression
            originalExpression = expression
            expression = self._standardize(expression)

            result = await loop.run_in_executor(None,
                sympy.factor,
                expression
            )
            result = str(result).replace("**", "^").replace("*", "")

            # Return the result in an embed
            embed = discord.Embed(
                title = "Factoring of `{}`".format(originalExpression),
                description = result,
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def factorial(self, message, parameters):
        """Gets the factorial of a number.\n

        number - The number to get the factorial of.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._factorial.getMinParameters():
            embed = getErrorMessage(self._factorial, Math.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._factorial.getMaxParameters():
            embed = getErrorMessage(self._factorial, Math.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            number = parameters[0]
        
            # Loop through number
            originalNumber = number
            try:
                number = int(number)

                for n in range(number - 1, 0, -1):
                    number *= n
                
                if number == 0:
                    number = 1

                # Setup embed
                embed = discord.Embed(
                    title = "Factorial of `{}`".format(originalNumber),
                    description = " ",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
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
            except:
                embed = getErrorMessage(self._factorial, Math.INVALID_INPUT)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def solve(self, message, parameters):
        """Solves an expression, or expressions, using sympy.\n

        expressions - The expressions to solve.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._solve.getMinParameters():
            embed = getErrorMessage(self._solve, Math.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            expressions = parameters
        
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
            varDict = await loop.run_in_executor(None,
                sympy.solve,
                expressions
            )
            varResult = {}
            result = ""

            # See if varDict is a list (multiple solutions)
            if type(varDict) == list:
                for solution in varDict:
                    for variable in solution:
                        if variable not in varResult:
                            varResult[variable] = []
                        varResult[variable].append(solution[variable])

            # See if varDict is a dict (single solutions)
            else:
                varResult = varDict

            for variable in varResult:
                result += "{} = {}\n".format(
                    variable, varResult[variable]
                )
            
            embed = discord.Embed(
                title = "Solution",
                description = "`{}`\n".format(originalExpression) + result,
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def substitute(self, message, parameters):
        """Substitutes an expression with variables using sympy.\n

        expression - The expression to substitute.\n
        variables - The variables to substitute in the expression.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._substitute.getMinParameters():
            embed = getErrorMessage(self._substitute, Math.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            expression = parameters[0]
            variables = parameters[1:]
        
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

            # There were no variables to go through
            if len(variables) == 0:
                embed = getErrorMessage(self._substitute, Math.NO_VARIABLES)
            
            # There are variables to go through
            else:

                # Standardize expression
                expression = self._standardize(expression)

                result = await loop.run_in_executor(None,
                    expression.subs,
                    variables
                )
                result = str(eval(str(result)))

                embed = discord.Embed(
                    title = "Subsitution of `{}`".format(originalExpression),
                    description = result,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def fibonacci(self, message, parameters):
        """Gets the fibonacci of a number.\n

        number - The number to get the fibonacci of.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._fibonacci.getMinParameters():
            embed = getErrorMessage(self._fibonacci, Math.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._fibonacci.getMaxParameters():
            embed = getErrorMessage(self._fibonacci, Math.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            number = parameters[0]

            embed = discord.Embed(
                title = "`{}{}` Fibonacci number".format(
                    number,
                    Math.APPENDAGES[str(number)[-1]]
                ),
                description = str(self._fibonacciHelper(number)),
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
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
    
    async def derivative(self, message, parameters):
        """Gets the derivative of an expression using sympy.\n

        expression - The expression to get the derivative of.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._derivative.getMinParameters():
            embed = getErrorMessage(self._derivative, Math.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            expression = " ".join(parameters)
        
            # Standardize expression
            originalExpression = expression
            expression = self._standardize(expression)

            result = await loop.run_in_executor(None,
                sympy.diff,
                expression
            )
            result = str(result).replace("**", "^").replace("*", "")

            embed = discord.Embed(
                title = "Derivative of `{}`".format(originalExpression),
                description = result,
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def integral(self, message, parameters):
        """Gets the integral of an expression using sympy.\n

        expression - The expression to get the integral of.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._integral.getMinParameters():
            embed = getErrorMessage(self._integral, Math.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            expression = " ".join(parameters)
        
            # Standardize expression
            originalExpression = expression
            expression = self._standardize(expression)

            result = await loop.run_in_executor(None,
                sympy.integrate,
                expression, x
            )
            result = str(result).replace("**", "^").replace("*", "")

            embed = discord.Embed(
                title = "Integral of `{}`".format(originalExpression),
                description = result,
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )

    def _standardize(self, expression):
        """Standardizes the expression so sympy can read it.\n

        expression - The expression to standardize.\n
        """

        # Standardize expressions using parse_expr
        return parse_expr(expression.replace("^", "**"), transformations = self._transformations)
    
    async def solveKinematics(self, message, parameters):
        """Solves for as many kinematics variables as possible.
        """

        # Check for too many parameters
        if len(parameters) > self._solveKinematics.getMaxParameters():
            embed = getErrorMessage(self._solveKinematics, Math.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            variables = {}
            
            # Iterate through variables and make sure each variable is valid
            for variable in parameters:

                # Get the variable and the value
                equals = variable.find("=")

                # See if there was a missing equals sign
                if equals == -1:
                    embed = getErrorMessage(self._solveKinematics, Math.MISSING_EQUALS)
                    break
                
                # There was no missing equals sign
                var   = variable[:equals]
                value = variable[equals + 1:]

                # Make sure value is a number
                try:
                    value = eval(value)
                except:
                    embed = getErrorMessage(self._solveKinematics, Math.INVALID_INPUT)
                    break

                variables[var] = value
            
            # Check if any variables is invalid
            if not Kinematics.isKinematicVariable(list(variables.keys())):
                embed = getErrorMessage(self._solveKinematics, Math.INVALID_PARAMETER)
            
            # All variables are valid; Give it to the solver
            else:
                result = Kinematics.solve(variables)

                # Separate displacement, velocity, and other variables
                fields = {
                    "Displacement": "X = {}\nXo = {}\nXf = {}".format(
                        result["X"], result["Xo"], result["Xf"]
                    ),
                    "Velocity": "V = {}\nVo = {}\nVf = {}".format(
                        result["V"], result["Vo"], result["Vf"]
                    ),
                    "Other": "a = {}\nt = {}".format(
                        result["a"], result["t"]
                    )
                }
                embed = discord.Embed(
                    title = "Linear Kinematics",
                    description = " ",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )

                for field in fields:
                    embed.add_field(
                        name = field,
                        value = fields[field],
                        inline = True
                    )
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs an Math Category command if it can.

        message - The Discord Message to parse.
        """

        # Make sure message starts with the prefix
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Iterate through commands
            for cmd in self.getCommands():
                if command in cmd.getAlternatives():

                    # Run the command but don't try running others
                    await self.run(message, cmd, cmd.getCommand(), message, parameters)
                    break

def setup(client):
    client.add_cog(Math(client))
