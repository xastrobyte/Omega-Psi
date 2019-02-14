class UnbalancedParentheses(Exception): pass
class MissingTruthValue(Exception): pass

class LogicVar:

    def __init__(self, *, value = None, has_not = False):
        self._value = value
        self._has_not = has_not
    
    def get_value(self):
        return self._value
    
    def has_not(self):
        return self._has_not
    
    def create_truth_table(self, truth_values = []):

        truth_evaluations = []

        # Only run this if there is a has_not
        if not self.has_not():
            return truth_evaluations
        
        # Iterate through truth values
        for truth_value in truth_values:
            evaluation = {
                "expression": "~" + self.get_value(),
                "truth_value": truth_value,
                "value": self.evaluate(truth_value)
            }
            if evaluation not in truth_evaluations:
                truth_evaluations.append(evaluation)
        
        return truth_evaluations
    
    def evaluate(self, truth_value = {}):
        if self.get_value() not in truth_value:
            raise MissingTruthValue("You need a truth value for the variable \"{}\"".format(self.get_value()))
        
        if self.has_not():
            return not truth_value[self.get_value()]
        
        return truth_value[self.get_value()]
    
    def __str__(self):
        if self.has_not():
            return "~" + self.get_value()

        return self.get_value()

class LogicNode:

    AND = "and"
    OR = "or"
    NOT = "not"
    IMPLIES = "implies"
    BICONDITIONAL = "biconditional"

    def __init__(self, *, operator = None, left = None, right = None, has_not = False):
        self._operator = operator

        if "value" in left:
            left = LogicVar(
                value = left["value"],
                has_not = left["has_not"]
            )
        
        else:
            left = LogicNode(
                operator = left["operator"], 
                left = left["left"], 
                right = left["right"],
                has_not = left["has_not"]
            )
        
        if "value" in right:
            right = LogicVar(
                value = right["value"],
                has_not = right["has_not"]
            )
        
        else:
            right = LogicNode(
                operator = right["operator"], 
                left = right["left"], 
                right = right["right"],
                has_not = right["has_not"]
            )

        self._left = left
        self._right = right
        self._has_not = has_not
    
    def get_operator(self):
        return self._operator
    
    def and_type(self):
        return self._operator == LogicNode.AND
    
    def or_type(self):
        return self._operator == LogicNode.OR
    
    def implies_type(self):
        return self._operator == LogicNode.IMPLIES
    
    def biconditional_type(self):
        return self._operator == LogicNode.BICONDITIONAL
    
    def has_not(self):
        return self._has_not
    
    def get_left(self):
        return self._left
    
    def get_right(self):
        return self._right
    
    def create_truth_table(self, truth_values = []):

        truth_evaluations = []

        # Get left evaluations
        left_evaluations = self.get_left().create_truth_table(truth_values)
        for left_evaluation in left_evaluations:
            if left_evaluation not in truth_evaluations:
                truth_evaluations.append(left_evaluation)
        
        # Get right evaluations
        right_evaluations = self.get_right().create_truth_table(truth_values)
        for right_evaluation in right_evaluations:
            if right_evaluation not in truth_evaluations:
                truth_evaluations.append(right_evaluation)
        
        # Iterate through all the truth values
        for truth_value in truth_values:
            
            # Evaluate self
            self_evaluation = self.evaluate(truth_value)
            self_evaluation = {
                "expression": str(self),
                "truth_value": truth_value,
                "value": self_evaluation
            }
            if self_evaluation not in truth_evaluations:
                truth_evaluations.append(self_evaluation)
        
        return truth_evaluations
    
    def evaluate(self, truth_value = {}, include_not = True):

        left = self.get_left().evaluate(truth_value)
        right = self.get_right().evaluate(truth_value)

        if self.and_type():
            if self.has_not():
                return not (left and right)
            return left and right
        
        if self.or_type():
            if self.has_not():
                return not (left or right)
            return left or right
    
        if self.implies_type():
            return not left or right
        
        if self.biconditional_type():
            return left == right
    
    def __str__(self):
        left = str(self.get_left())
        if type(self.get_left()) == LogicNode:
            if not self.get_left().has_not():
                left = "(" + left + ")"
        right = str(self.get_right())
        if type(self.get_right()) == LogicNode:
            if not self.get_right().has_not():
                right = "(" + right + ")"
        
        if self.and_type():
            operator = "^"
        elif self.or_type():
            operator = "v"
        elif self.implies_type():
            operator = "->"
        elif self.biconditional_type():
            operator = "<->"

        if self.has_not():
            return "~({} {} {})".format(
                left, operator, right
            )

        return "{} {} {}".format(
            left, operator, right
        )

class LogicTree:
    def __init__(self, expression):
        self._expression = expression
        self._variables = []
        self._root = None
        self.parse()
    
    def get_expression(self):
        return self._expression
    
    def get_variables(self):
        return self._variables
    
    def parse(self):
        exp = parse_expression(self.get_expression())
        expression = exp["expression"]
        variables = exp["variables"]

        self._variables = variables
        self._root = LogicNode(
            operator = expression["operator"],
            left = expression["left"],
            right = expression["right"],
            has_not = expression["has_not"]
        )
    
    def show_when_true(self):
        pass
    
    def show_when_false(self):
        pass
    
    def make_table(self):

        lines = []
        result = ""

        # Setup truth table
        evaluations = self.create_truth_table()
        table_dict = {}
        for evaluation in evaluations:
            if evaluation["expression"] not in table_dict:
                table_dict[evaluation["expression"]] = []
            
            table_dict[evaluation["expression"]].append(evaluation["value"])

        # Add column labels
        count = 0
        length = len(table_dict)
        for column in table_dict:
            line = "| " + column.center(len(column))
            if count > 0:
                line = " " + line
            if count == length - 1:
                line += " |"
            result += line
            count += 1
        lines.append(result)
        result = ""

        # Add label split lin
        count = 0
        for column in table_dict:
            line = "+" + "-".center(len(column) + 1, "-")
            if count > 0:
                line = "-" + line
            if count == length - 1:
                line += "-+"
            result += line
            count += 1
        lines.append(result)
        result = ""

        # Add truth values
        max_truths = -1
        for column in table_dict:
            if max_truths == -1:
                max_truths = len(table_dict[column])
        
        for index in range(max_truths):
            count = 0
            for column in table_dict:
                value = table_dict[column][index]
                value = "T" if value == True else ("F" if value == False else "-")
                line = "| " + value.center(len(column))
                if count > 0:
                    line = " " + line
                if count == length - 1:
                    line += " |"
                result += line
                count += 1
            lines.append(result)
            result = ""

        return lines

    def create_truth_table(self):
        
        # Create every possible truth combination for all variables
        truth_values = []

        # Iterate through 2 ** variable_amount possible combinations
        for value in range(2 ** len(self.get_variables())):

            # Iterate through all variables
            value_dict = {}
            for index in range(len(self.get_variables())):

                # Get the power based off of the variable's index in the list
                power = len(self.get_variables()) - index - 1
                variable = self.get_variables()[index]

                # Get the truth value using the get_truth_value function
                value_dict[variable] = get_truth_value(value, power)
            
            truth_values.append(value_dict)
        
        # Create truth values for other operations
        # For example, if there is a "~a", then there will be a column designated to that.
        #              if there is a "~(a v b)", then there will be a column designated to that
        #                 as well as the "a v b" part.
        truth_evaluations = []

        root_truth_evaluations = self._root.create_truth_table(truth_values)

        # Add all the truth evaluations from the root
        for truth_evaluation in root_truth_evaluations:
            if truth_evaluation not in truth_evaluations:
                truth_evaluations.append(truth_evaluation)
            
        # Add all the truth values as evaluations
        for truth_value in truth_values:
            for truth_variable in truth_value:
                truth_evaluation = {
                    "expression": truth_variable,
                    "truth_value": {
                        truth_variable: truth_value[truth_variable]
                    },
                    "value": truth_value[truth_variable]
                }
                
                truth_evaluations.append(truth_evaluation)
        
        truth_evaluations = sorted(truth_evaluations, key = lambda i: len(i["expression"])) 
        
        return truth_evaluations

def get_truth_value(value, power):
    return ((value // 2 ** power) % 2) == 0

operators = {
    "or": "v",
    "||": "v",
    "v": "v",
    "and": "^",
    "&&": "^",
    "^": "^",
    "not ": "~",
    "not": "~",
    "!": "~",
    "~": "~",
    "<->": "-",
    "->": ">",
    ">": ">"
}

def parse_expression(expression, has_not = False):
    """Separate important parts of a logical expression to evaluate each individually.

    Parameters:
        expression (str): The expression to parse.
    """

    # Trim the expression to remove extra spaces at the start and end
    expression = expression.strip()

    # Go through all operators and replace expressions
    for operator in operators:
        expression = expression.replace(operator, operators[operator])

    # Loop through and find any ^ (AND) or v (OR) operators as expressions
    has_not = has_not
    left = None
    operator = None
    right = None
    variables = []

    parent_depth = 0
    last = 0

    char_has_not = False

    for index in range(len(expression)):
        char = expression[index]

        # Check for open parenthesis
        if char == "(":
            if parent_depth == 0:
                last = index + 1
            parent_depth += 1
        
        # Check for close parenthesis
        elif char == ")":
            parent_depth -= 1

            # Parse expression if parenthesis depth reaches 0
            if parent_depth == 0:

                # Check if there is a ~ (NOT) operator directly in front of the variable
                if last - 1 > 0:
                    if expression[last - 2] == "~":
                        has_not = True

                exp = parse_expression(expression[last:index], has_not)

                # Check if there is no operator; Must be left side
                if operator == None:
                    left = exp["expression"]

                # Check if there is an operator; Must be right side
                else:
                    right = exp["expression"]

        if parent_depth == 0:

            # Check for operator only if not within a parenthesis
            if char in ['^', 'v', ">", "-"]:

                # Check if operator doesn't exist yet
                if operator == None:
                    if char == "^":
                        operator = LogicNode.AND
                    elif char == "v":
                        operator = LogicNode.OR
                    elif char == ">":
                        operator = LogicNode.IMPLIES
                    elif char == "-":
                        operator = LogicNode.BICONDITIONAL
                    
                # Operator exists; String of logical expressions exists
                # Make the left, operator, right into the left expression
                else:
                    left = {
                        "has_not": has_not,
                        "left": left,
                        "operator": operator,
                        "right": right
                    }

                    has_not = False
                    if char == "^":
                        operator = LogicNode.AND
                    elif char == "v":
                        operator = LogicNode.OR
                    elif char == ">":
                        operator = LogicNode.IMPLIES
                    right = None
                
        # Check for variable only if not within a parenthesis
        if ord(char) in range(ord('a'), ord('z') + 1) and ord(char) != ord('v'):

            # See if there is a ~ (NOT) operator directly in front of the variable
            if index > 0:
                if expression[index - 1] == "~":
                    char_has_not = True
                else:
                    char_has_not = False

            # Check if there is no operator; Must be left side
            if operator == None:
                left = {
                    "has_not": char_has_not,
                    "value": char
                }
            
            # Check if there is an operator; Must be right side
            else:
                right = {
                    "has_not": char_has_not,
                    "value": char
                }
            
            if char not in variables:
                variables.append(char)
            
    if parent_depth != 0:
        raise UnbalancedParentheses("You have a missing parenthesis somewhere.")
    
    variables.sort()

    # Check if the expression is a single expression wrapped in parenthesese
    if operator == right == None:
        has_not = left["has_not"]
        operator = left["operator"]
        right = left["right"]
        left = left["left"]

    return {
        "expression": {
            "has_not": has_not,
            "left": left,
            "operator": operator,
            "right": right
        },
        "variables": variables
    }