from util.math.utils import unitFy

import math

class Kinematics:
    """A static class that holds methods to solve for Linear Kinematic Physics
    """

    VALID_VARIABLES = [
        "X", "Xo", "Xf",
        "V", "Vo", "Vf",
        "a", "t"
    ]

    @staticmethod
    def isKinematicVariable(variableList):
        """Checks if any variable inside a variable list is invalid.

        Parameters:
            variableList (list): The list of variables to go through.
        """

        for variable in variableList:
            if variable not in Kinematics.VALID_VARIABLES:
                return False
            
        return True
    
    @staticmethod
    def getVariables(variablesDict):
        """Returns all variables that are in a dictionary

        Parameters:
            variablesDict (dict): The dictionary to get the variables from.
        """

        X = Xo = Xf = None
        V = Vo = Vf = None
        a = t = None

        if "X" in variablesDict:
            X = variablesDict["X"]
        if "Xo" in variablesDict:
            Xo = variablesDict["Xo"]
        if "Xf" in variablesDict:
            Xf = variablesDict["Xf"]
        
        if "V" in variablesDict:
            V = variablesDict["V"]
        if "Vo" in variablesDict:
            Vo = variablesDict["Vo"]
        if "Vf" in variablesDict:
            Vf = variablesDict["Vf"]
        
        if "a" in variablesDict:
            a = variablesDict["a"]
        if "t" in variablesDict:
            t = variablesDict["t"]
        
        return X, Xo, Xf, V, Vo, Vf, a, t

    @staticmethod
    def solveForXo(variablesDict = None, *, X = None, Xf = None, V = None, Vo = None, Vf = None, a = None, t = None, rounding = 3):
        """Tries to solve for the initial position given the other 5 kinematics variables.

        This can be used for both horizontal and vertical kinematics.

        Parameters:
            variablesDict (dict): A dictionary of variables to use.
            X (float): The position of an object in meters (Useful for displacement).
            Xf (float): The final position of an object in meters.
            V (float): The velocity of an object in meters / second (Useful for constant velocity).
            Vo (float): The initial velocity of an object in meters / second.
            Vf (float): The final velocity of an object in meters / second.
            a (float): The acceleration of an object in meters / second^2.
            t (float): The time of the analysis in seconds.
            rounding (int): The decimal places to round it to.

        Returns:
            None: If the initial position could not be solved.
            value (float): The value of the initial position.
        """

        # Get variables from variable dict if possible
        if variablesDict != None:
            X, Xo, Xf, V, Vo, Vf, a, t = Kinematics.getVariables(variablesDict)

        # Check if only X is solved
        # If so, Xo is at 0
        if X != None and Xf == None:
            return 0

        # Check if X and Xf are solved
        # If so, subtract X from Xf
        elif X != None and Xf != None:
            solution = Xf - X
            if rounding != -1:
                return round(solution, rounding)
            return solution

        # Check if Xf, V, and t are solved
        # If so, use Xo = -Vt + Xf
        elif Xf != None and V != None and a != None:
            equation = f"-V*t + Xf"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xf, Vo, Vf and t are solved
        # If so, use Xo = Xf - 1/2[Vf + Vo]t
        elif Xf != None and Vo != None and Vf != None and t != None:
            equation = f"Xf - ((1/2)*t(Vf + Vo)*t)"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xf, Vo, Vf, and a are solved
        # If so, use Xo = -(Vf^2 - Vo^2) / (2a) + Xf
        elif Xf != None and Vo != None and Vf != None and a != None:
            equation = f"-((Vf**2 - Vo**2) / (2*a)) + Xf"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xf, Vo, a, and t are solved
        # If so, use Xo = Xf - Vot - 1/2at^2
        elif Xf != None and Vo != None and a != None and t != None:
            equation = f"Xf - Vo*t - (1/2)*a*t**2"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xf, Vf, a, and t are solved
        # First, solve for Vo
        # Then use recursion to call this method
        elif Xf != None and Vf != None and a != None and t != None:
            Vo = Kinematics.solveForVo(Xf = Xf, Vf = Vf, a = a, t = t, rounding = -1)
            solution = Kinematics.solveForXo(Xf = Xf, Vo = Vo, Vf = Vf, a = a, t = t, rounding = -1)
            if rounding != -1:
                return round(solution, rounding)
            return solution

        # Xo cannot be solved
        return None
        

    @staticmethod
    def solveForXf(variablesDict = None, *, X = None, Xo = None, V = None, Vo = None, Vf = None, a = None, t = None, rounding = 3):
        """Tries to solve for the initial position given the other 5 kinematics variables.

        This can be used for both horizontal and vertical kinematics.

        Parameters:
            variablesDict (dict): A dictionary of variables to use.
            X (float): The position of an object in meters (Useful for displacement).
            Xf (float): The final position of an object in meters.
            V (float): The velocity of an object in meters / second (Useful for constant velocity).
            Vo (float): The initial velocity of an object in meters / second.
            Vf (float): The final velocity of an object in meters / second.
            a (float): The acceleration of an object in meters / second^2.
            t (float): The time of the analysis in seconds.
            rounding (int): The decimal places to round it to.

        Returns:
            None: If the initial position could not be solved.
            value (float): The value of the final position.
        """

        # Get variables from variable dict if possible
        if variablesDict != None:
            X, Xo, Xf, V, Vo, Vf, a, t = Kinematics.getVariables(variablesDict)

        # Check if only X is solved
        # If so, return X
        if X != None and Xo == None:
            return X

        # Check if X and Xo are solved
        # If so, add X to Xo
        elif X != None and Xo != None:
            solution = Xo + X
            if rounding != -1:
                return round(solution, rounding)
            return solution

        # Check if Xo, V, and t are solved
        # If so, use Xf = Xo + Vt
        elif Xo != None and V != None and t != None:
            equation = f"Xo + V*t"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Vo, Vf, and t are solved
        # If so, use Xf = Xo + 1/2[Vf + Vo]t
        elif Xo != None and Vo != None and Vf != None and t != None:
            equation = f"Xo + (1/2)*(Vf + Vo)*t"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Vo, Vf, and a are solved
        # If so, use Xf = (Vf^2 - Vo^2) / (2a) + Xo
        elif Xo != None and Vo != None and Vf != None and a != None:
            equation = f"((Vf**2 - Vo**2) / (2*a)) + Xo"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Vo, a, and t are solved
        # If so, use Xf = Xo + Vot + 1/2at^2
        elif Xo != None and Vo != None and a != None and t != None:
            equation = f"Xo + Vo*t + (1/2)*a*t**2"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Vf, a, and t are solved
        # First, solve for Vo
        # Then use recursion to call this method
        elif Xo != None and Vf != None and a != None and t != None:
            Vo = Kinematics.solveForVo(Xo = Xo, Vf = Vf, a = a, t = t, rounding = -1)
            solution = Kinematics.solveForXf(Xo = Xo, Vo = Vo, Vf = Vf, a = a, t = t, rounding = -1)
            if rounding != -1:
                return round(solution, rounding)
            return solution

        # Xf cannot be solved
        return None

    @staticmethod
    def solveForVo(variablesDict = None, *, X = None, Xo = None, Xf = None, V = None, Vf = None, a = None, t = None, rounding = 3):
        """Tries to solve for the initial velocity given the other 5 kinematics variables.

        This can be used for both horizontal and vertical kinematics.

        Parameters:
            variablesDict (dict): A dictionary of variables to use.
            X (float): The position of an object in meters (Useful for displacement).
            Xo (float): The initial position of an object in meters.
            Xf (float): The final position of an object in meters.
            V (float): The velocity of an object in meters / second (Useful for constant velocity).
            Vf (float): The final velocity of an object in meters / second.
            a (float): The acceleration of an object in meters / second^2.
            t (float): The time of the analysis in seconds.
            rounding (int): The decimal places to round it to.

        Returns:
            None: If the initial velocity could not be solved.
            value (float): The value of the initial velocity.
        """

        # Get variables from variable dict if possible
        if variablesDict != None:
            X, Xo, Xf, V, Vo, Vf, a, t = Kinematics.getVariables(variablesDict)

        # Check if V is solved
        # If so, return it
        if V != None:
            if rounding != -1:
                return round(V, rounding)
            return V

        # Check if Vf, a, and t are solved
        # If so, use Vo = Vf - at
        elif Vf != None and a != None and t != None:
            equation = f"Vf - a*t"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Xf, Vf, and t are solved
        # If so, use Vo = = 2(Xf - Xo) / t - Vf
        elif Xo != None and Xf != None and Vf != None and t != None:
            equation = f"2*(Xf - Xo) / t - Vf"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Xf, a, and t are solved
        # If so, use Vo = (Xf - Xo - 1/2at^2) / t
        elif Xo != None and Xf != None and a != None and t != None:
            equation = f"(Xf - Xo - (1/2)*a*t**2) / t"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)
        
        # Check if Xo, Xf, Vf, and a are solved
        # If so, use Vo = sqrt(Vf^2 - 2a(Xf - Xo))
        elif Xo != None and Xf != None and Vf != None and a != None:
            equation = f"(Vf**2) - 2*a*(Xf - Xo)"
            root = math.sqrt(eval(equation))

            # Check if displacement is negative, make root negative
            if (Xf - Xo) < 0:
                root = - root

            if rounding != -1:
                return round(root, rounding)
            return root
        
        # Vo cannot be solved
        return None

    @staticmethod
    def solveForVf(variablesDict = None, *, X = None, Xo = None, Xf = None, V = None, Vo = None, a = None, t = None, rounding = 3):
        """Tries to solve for the final velocity given the other 5 kinematics variables.

        This can be used for both horizontal and vertical kinematics.

        Parameters:
            variablesDict (dict): A dictionary of variables to use.
            X (float): The position of an object in meters (Useful for displacement).
            Xo (float): The initial position of an object in meters.
            Xf (float): The final position of an object in meters.
            V (float): The velocity of an object in meters / second (Useful for constant velocity).
            Vo (float): The initial velocity of an object in meters / second.
            a (float): The acceleration of an object in meters / second^2.
            t (float): The time of the analysis in seconds.
            rounding (int): The decimal places to round it to.

        Returns:
            None: If the final velocity could not be solved.
            value (float): The value of the final velocity.
        """

        # Get variables from variable dict if possible
        if variablesDict != None:
            X, Xo, Xf, V, Vo, Vf, a, t = Kinematics.getVariables(variablesDict)

        # Check if V is solved
        # If so, return it
        if V != None:
            if rounding != -1:
                return round(V, rounding)
            return V

        # Check if Vo, a, and t are solved
        # If so, use Vf = Vo + at
        elif Vo != None and a != None and t != None:
            equation = f"Vo + a*t"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Xf, and t are solved
        # If so, use V = (Xf - Xo) / t
        elif Xo != None and Xf != None and t != None:
            equation = f"(Xf - Xo) / t"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Xf, Vo, and t are solved
        # If so, use Vf = 2(Xf - Xo) / t - Vo
        elif Xo != None and Xf != None and Vo != None and t != None:
            equation = f"2*(Xf - Xo) / t - Vo"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Xf, Vo, and a are solved
        # If so, use Vf = sqrt(Vo^2 + 2a(Xf - Xo))
        elif Xo != None and Xf != None and Vo != None and a != None:
            equation = f"Vo**2 + 2*a*(Xf - Xo)"
            root = math.sqrt(eval(equation))

            # Check if displacement is negative, make root negative
            if (Xf - Xo) < 0:
                root = - root

            if rounding != -1:
                return round(root, rounding)
            return root

        # Check if Xo, Xf, a, and t are solved
        # First, solve for Vo
        # Then use recursion to call this method
        elif Xo != None and Xf != None and a != None and t != None:
            Vo = Kinematics.solveForVo(Xo = Xo, Xf = Xf, a = a, t = t, rounding = -1)
            solution = Kinematics.solveForVf(Xo = Xo, Xf = Xf, Vo = Vo, a = a, t = t, rounding = -1)
            if rounding != -1:
                return round(solution, rounding)
            return solution

        # Vf cannot be solved
        return None

    @staticmethod
    def solveForA(variablesDict = None, *, X = None, Xo = None, Xf = None, V = None, Vo = None, Vf = None, t = None, rounding = 3):
        """Tries to solve for the acceleration given the other 5 kinematics variables.

        This can be used for both horizontal and vertical kinematics.

        Parameters:
            variablesDict (dict): A dictionary of variables to use.
            X (float): The position of an object in meters (Useful for displacement).
            Xo (float): The initial position of an object in meters.
            Xf (float): The final position of an object in meters.
            V (float): The velocity of an object in meters / second (Useful for constant velocity).
            Vo (float): The initial velocity of an object in meters / second.
            Vf (float): The final velocity of an object in meters / second.
            t (float): The time of the analysis in seconds.
            rounding (int): The decimal places to round it to.

        Returns:
            None: If the acceleration could not be solved.
            value (float): The value of the acceleration.
        """

        # Get variables from variable dict if possible
        if variablesDict != None:
            X, Xo, Xf, V, Vo, Vf, a, t = Kinematics.getVariables(variablesDict)

        # If given X, Xo is 0, Xf is X
        if X != None:
            Xo = 0
            Xf = X

        # If given V, Vo is V, Vf is V
        if V != None:
            Vo = V
            Vf = V

        # Check if Vo, Vf, and t are solved
        # If so, use a = (Vf - Vo) / t
        if Vo != None and Vf != None and t != None:
            equation = f"(Vf - Vo) / t"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Xf, Vo, and t are solved
        # If so, use a = 2(Xf - Xo - Vot) / t^2
        elif Xo != None and Xf != None and Vo != None and t != None:
            equation = f"2*(Xf - Xo - Vo*t) / t**2"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Xf, Vo, and Vf are solved
        # If so, use a = (Vf^2 - Vo^2) / 2(Xf - Xo)
        elif Xo != None and Xf != None and Vo != None and Vf != None:
            equation = f"(Vf**2 - Vo**2) / (2*(Xf - Xo))"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Xf, Vf, and t are solved
        # First, solve for Vo
        # Then use recursion to call this method
        elif Xo != None and Xf != None and Vf != None and t != None:
            Vo = Kinematics.solveForVo(Xo = Xo, Xf = Xf, Vf = Vf, t = t, rounding = -1)
            solution = Kinematics.solveForA(Xo = Xo, Xf = Xf, Vo = Vo, Vf = Vf, t = t, rounding = -1)
            if rounding != -1:
                return round(solution, rounding)
            return solution

        # a cannot be solved
        return None

    @staticmethod
    def solveForT(variablesDict = None, *, X = None, Xo = None, Xf = None, V = None, Vo = None, Vf = None, a = None, rounding = 3):
        """Tries to solve for the time given the other 5 kinematics variables.

        This can be used for both horizontal and vertical kinematics.

        Parameters:
            variablesDict (dict): A dictionary of variables to use.
            X (float): The position of an object in meters (Useful for displacement).
            Xo (float): The initial position of an object in meters.
            Xf (float): The final position of an object in meters.
            V (float): The velocity of an object in meters / second (Useful for constant velocity).
            Vo (float): The initial velocity of an object in meters / second.
            Vf (float): The final velocity of an object in meters / second.
            a (float): The acceleration of an object in meters / second^2.
            rounding (int): The decimal places to round it to.

        Returns:
            None: If the time could not be solved.
            value (float): The value of the time.
        """

        # Get variables from variable dict if possible
        if variablesDict != None:
            X, Xo, Xf, V, Vo, Vf, a, t = Kinematics.getVariables(variablesDict)

        # If X is given, Xo is 0, Xf is X
        if X != None:
            Xo = 0
            Xf = X

        # If V is given, Vo is V, Vf is V
        if V != None:
            Vo = V
            Vf = V

        # Check if Vo, Vf, and a are solved
        # If so, use t = (Vf - Vo) / a
        if Vo != None and Vf != None and a != None:
            equation = f"(Vf - Vo) / a"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Xf, and V are solved
        elif Xo != None and Xf != None and V != None:
            equation = f"(Xf - Xo) / V"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Xf, Vo, and Vf are solved
        # If so, use t = 2(Xf - Xo) / (Vf - Vo)
        elif Xo != None and Xf != None and Vo != None and Vf != None:
            equation = f"2*(Xf - Xo) / (Vf + Vo)"
            if rounding != -1:
                return round(eval(equation), rounding)
            return eval(equation)

        # Check if Xo, Xf, Vo, and a are solved
        # First, solve for Vf
        # Then use recursion to call this method
        elif Xo != None and Xf != None and Vo != None and a != None:
            Vf = Kinematics.solveForVf(Xo = Xo, Xf = Xf, Vo = Vo, a = a, rounding = -1)
            solution = Kinematics.solveForT(Xo = Xo, Xf = Xf, Vo = Vo, Vf = Vf, a = a, rounding = -1)
            if rounding != -1:
                return round(solution, rounding)
            return solution

        # Check if Xo, Xf, Vf, and a are solved
        # First, solve for Vo
        # Then use recursion to call this method
        elif Xo != None and Xf != None and Vf != None and a != None:
            Vo = Kinematics.solveForVo(Xo = Xo, Xf = Xf, Vf = Vf, a = a, rounding = rounding)
            solution = Kinematics.solveForT(Xo = Xo, Xf = Xf, Vo = Vo, Vf = Vf, a = a, rounding = rounding)
            if rounding != -1:
                return round(solution, rounding)
            return solution

        # t could not be solved
        return None

    @staticmethod
    def solve(variablesDict = None, *, X = None, Xo = None, Xf = None, V = None, Vo = None, Vf = None, a = None, t = None, rounding = 3):
        """"Tries to solve for all the kinematic variables.

        This can be used for both horizontal and vertical kinematics.

        Parameters:
            variablesDict (dict): A dictionary of variables to use.
            X (float): The position of an object in meters (Useful for displacement).
            Xo (float): The initial position of an object in meters.
            Xf (float): The final position of an object in meters.
            V (float): The velocity of an object in meters / second (Useful for constant velocity).
            Vo (float): The initial velocity of an object in meters / second.
            Vf (float): The final velocity of an object in meters / second.
            a (float): The acceleration of an object in meters / second^2.
            t (float): The time of the analysis in seconds.
            rounding (int): The decimal places to round it to.

        Returns:
            values (dict): The values of each kinematic variable that can be solved.
        """

        # Get variables from variable dict if possible
        if variablesDict != None:
            X, Xo, Xf, V, Vo, Vf, a, t = Kinematics.getVariables(variablesDict)

        # Try solving for each value until no values were solved
        # - Keep track of previous values to test for a change
        prevX  = X
        prevXo = Xo
        prevXf = Xf
        
        prevV  = V
        prevVo = Vo
        prevVf = Vf

        preva  = a
        prevt  = t

        valueChanged = True
        while valueChanged:
            valueChanged = False

            # Displacement Values
            if Xo == None:
                Xo = Kinematics.solveForXo(X = X, Xf = Xf, V = V, Vo = Vo, Vf = Vf, a = a, t = t, rounding = rounding)
            if Xo != prevXo:
                prevXo = Xo
                valueChanged = True

            if Xf == None:
                Xf = Kinematics.solveForXf(X = X, Xo = Xo, V = V, Vo = Vo, Vf = Vf, a = a, t = t, rounding = rounding)
            if Xf != prevXf:
                prevXf = Xf
                valueChanged = True

            if Xo != None and Xf != None:
                X = Xf - Xo
            if X != prevX:
                prevX = X
                valueChanged = True

            # Velocity Values
            if Vo == None:
                Vo = Kinematics.solveForVo(X = X, Xo = Xo, Xf = Xf, V = V, Vf = Vf, a = a, t = t, rounding = rounding)
            if Vo != prevVo:
                prevVo = Vo
                valueChanged = True

            if Vf == None:
                Vf = Kinematics.solveForVf(X = X, Xo = Xo, Xf = Xf, V = V, Vo = Vo, a = a, t = t, rounding = rounding)
            if Vf != prevVf:
                prevVf = Vf
                valueChanged = True

            if Vo != None and Vf != None and Vo == Vf:
                V = Vo
            if V != prevV:
                prevV = V
                valueChanged = True

            # Acceleration and Time
            if a == None:
                a = Kinematics.solveForA(X = X, Xo = Xo, Xf = Xf, V = V, Vo = Vo, Vf = Vf, t = t, rounding = rounding)
            if a != preva:
                preva = a
                valueChanged = True
                
            if t == None:
                t = Kinematics.solveForT(X = X, Xo = Xo, Xf = Xf, V = V, Vo = Vo, Vf = Vf, a = a, rounding = rounding)
            if t != prevt:
                prevt = t
                valueChanged = True

        return unitFy({
            "X": X,
            "Xo": Xo,
            "Xf": Xf,
            "V": V,
            "Vo": Vo,
            "Vf": Vf,
            "a": a,
            "t": t
        })