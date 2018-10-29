from util.file.omegaPsi import OmegaPsi
from util.utils import censor

from functools import wraps
from random import choice as choose

import discord, signal

class Error:
    
    def __init__(self, errorDict):
        """Creates an Error object for a Command.\n

        errorDict - The dictionary that holds the error messages for a Command.\n

        All Error Dictionaries must include the following tags:\n
         - \"messages\" - The error messages for this error.\n
        """

        # Load messages
        self._messages = errorDict["messages"]

    def getMessage(self):
        """Returns a random error message for this error
        """
        return choose(self._messages)
    
    def getMessages(self):
        """Returns the error messages for this error
        """
        return self._messages

class Accepted:

    def __init__(self, acceptedDict):
        """Creates an Accepted parameter object for a Command.\n

        acceptedDict - The dictionary that holds the accepted parameter info for a Command.\n

        All Accepted Dictionaries must include the following required tags:\n
         - \"alternatives\" - The alternatives for an accepted parameter.\n
         - \"info\" - The description of the accepted parameter.\n
        """
        
        # Load Alternatives
        self._alternatives = acceptedDict["alternatives"]

        # Load Info
        self._info = acceptedDict["info"]
    
    def getAlternatives(self):
        """Returns the alternatives for the accepted parameter.\n
        """
        return self._alternatives
    
    def getInfo(self):
        """Returns the info about the accepted parameter.\n
        """
        return self._info

class Parameter:

    def __init__(self, parameterDict):
        """Creates a Parameter object for a Command.\n

        parameterDict - The dictionary that holds the parameter info for a Command.\n

        All Parameter Dictionaries must include the following required tags:\n
         - \"optional\" - Whether or not the parameter is optional.\n
         - \"info\" - The description of the parameter.\n
        
        All Parameter Dictionaries can include the following optional tags:\n
         - \"accepted\" - A dictionary of accepted parameter names. If left empty, it is up to you to put in the logic behind it.\n
        """

        # Load Optional
        self._optional = parameterDict["optional"]

        # Load Info
        self._info = parameterDict["info"]

        # Load Accepted Parameters
        self._accepted = {}
        if "accepted" in parameterDict:
            for accepted in parameterDict["accepted"]:
                self._accepted[accepted] = Accepted(parameterDict["accepted"][accepted])
    
    def isOptional(self):
        """Returns whether or not the parameter is optional.\n
        """
        return self._optional
    
    def getInfo(self):
        """Returns the info for this parameter.\n
        """
        return self._info
    
    def getAcceptedParameters(self):
        """Returns the accepted parameters for this parameter.\n
        """
        return self._accepted
    
    def getAcceptedParameter(self, parameter):
        """Returns a specific accepted parameter for this parameter.\n

        parameter - The parameter or alternative to get an accepted parameter for.\n
        """

        # Iterate through accepted parameters
        for param in self._accepted:
            if parameter in self._accepted[param].getAlternatives():
                return self._accepted[param]
        
        return None

class Command:

    def __init__(self, commandDict):
        """Creates a Command object.\n

        All Command Dictionaries must include the following required tags:\n
         - \"alternatives\" - The alternatives for the Command.\n
         - \"info\" - The description of the Command.\n
        
        All Command Dictionaries can include the following optional tags:\n
         - \"restriction_info\" - More info on any restrictions the command has.\n
         - \"errors\" - The Errors that can happen in a Command.\n
         - \"parameters\" - The Parameters that a Command accepts.\n
         - \"run_in_private\" - Whether or not the Command can be run in a private message.\n
         - \"can_be_deactivated\" - Whether or not the Command can be deactivated.\n
         - \"server_moderator_only\" - Whether or not the Command can only be run by a server moderator.\n
         - \"bot_moderator_only\" - Whether or not the Command can only be run by a bot moderator.\n
        """

        # Load Alternatives
        self._alternatives = commandDict["alternatives"]

        # Load Info
        self._info = commandDict["info"]

        # Load Restriction Info
        self._restriction_info = None
        if "restriction_info" in commandDict:
            self._restriction_info = commandDict["restriction_info"]

        # Load Errors
        self._errors = {}
        if "errors" in commandDict:
            for error in commandDict["errors"]:
                self._errors[error] = Error(commandDict["errors"][error])
        
        # Load Parameters 
        self._parameters = {}
        if "parameters" in commandDict:
            for parameter in commandDict["parameters"]:
                self._parameters[parameter] = Parameter(commandDict["parameters"][parameter])
        
        # Load Run In Private
        self._run_in_private = True
        if "run_in_private" in commandDict:
            self._run_in_private = commandDict["run_in_private"]
        
        # Load Can Be Deactivated
        self._can_be_deactivated = True
        if "can_be_deactivated" in commandDict:
            self._can_be_deactivated = commandDict["can_be_deactivated"]
        
        # Load Server Moderator Only
        self._server_moderator_only = False
        if "server_moderator_only" in commandDict:
            self._server_moderator_only = commandDict["server_moderator_only"]

        # Load Bot Moderator Only
        self._bot_moderator_only = False
        if "bot_moderator_only" in commandDict:
            self._bot_moderator_only = commandDict["bot_moderator_only"]
    
    def getAlternatives(self):
        """Returns the alternatives for the Command.\n
        """
        return self._alternatives
    
    def getInfo(self):
        """Returns the info for the Command.\n
        """
        return self._info
    
    def getRestrictionInfo(self):
        """Returns the restriction info for the Command.\n
        """
        return self._restriction_info
    
    def getErrors(self):
        """Returns the Errors for the Command.\n
        """
        return self._errors
    
    def getError(self, error):
        """Returns a specific Error for the Command.\n

        error - The Error to get.\n
        """
        return self._errors[error]
    
    def addError(self, errorName, errorDict):
        """Adds an Error to the Command.\n

        errorDict - The dictionary of the Error to add.\n
        """
        self._errors[errorName] = Error(errorDict)
    
    def getParameters(self):
        """Returns the Parameters for the Command.\n
        """
        return self._parameters
    
    def getParameter(self, placeholder):
        """Returns a Placeholder Parameter for the Command.\n

        placeholder - The Placeholder Parameter to get.\n
        """
        return self._parameters[placeholder]
    
    def getAcceptedParameters(self, placeholder):
        """Returns the Accepted Parameters for a Placeholder Parameter

        placeholder - The Placeholder Parameter of the Accepted Parameters to get.\n
        """
        return self._parameters[placeholder].getAcceptedParameters()
    
    def getAcceptedParameter(self, placeholder, accepted):
        """Returns a specific Accepted Parameter for a Placeholder Parameter

        placeholder - The Placeholder Parameter of the Accepted Parameter to get.\n
        accepted - The Accepted Parameter to get.\n
        """
        return self._parameters[placeholder].getAcceptedParameter(accepted)
    
    def canBeRunInPrivate(self):
        """Returns whether or not the Command can be run in a private message.\n
        """
        return self._run_in_private
    
    def canBeDeactivated(self):
        """Returns whether or not the Command can be deactivated.\n
        """
        return self._can_be_deactivated
    
    def isServerModeratorCommand(self):
        """Returns whether or not the Command can be run by a Server Moderator only.\n
        """
        return self._server_moderator_only
    
    def isBotModeratorCommand(self):
        """Returns whether or not the Command can be run by a Bot Moderator only.\n
        """
        return self._bot_moderator_only
    
    def getHelp(self, *, inDepth = False, isNSFW = False):
        """Returns the text that helps a reader understand what the command does.\n

        Keyword Arguments:\n
         - inDepth - Whether or not to be in-depth with the Command information.\n
         - isNSFW - Whether or not to return NSFW results.\n
        """

        # See if inDepth
        if inDepth:

            # Setup Placeholder Parameters Text
            placeholderParameters = []
            for parameter in self.getParameters():
                placeholderParameters.append("{}{}{}".format(
                    "[" if self.getParameters()[parameter].isOptional() else "<",
                    parameter,
                    "]" if self.getParameters()[parameter].isOptional() else ">"
                ))
            placeholders = " ".join(placeholderParameters)
            
            # Setup Embed
            embed = discord.Embed(
                title = "{}".format(
                    censor(self._alternatives[0], True) if not isNSFW else self._alternatives[0]
                ),
                description = "{}\n`{} {}` - {}\n".format(
                    ("```diff\n-" + self._restriction_info + "\n```") if self._restriction_info != None else "",
                    censor(" | ".join(self.getAlternatives()), True) if not isNSFW else " | ".join(self.getAlternatives()),
                    censor(placeholders) if not isNSFW else placeholders,
                    censor(self.getInfo()) if not isNSFW else self.getInfo()
                ),
                color = 0x00FF80
            )

            # Setup Accepted Parameter Fields
            acceptedParameters = {}
            for parameter in self.getParameters():
                parameterName = parameter
                parameterObject = self.getParameters()[parameter]

                # Only add if there are accepted parameters
                if len(parameterObject.getAcceptedParameters()) > 0:
                    acceptedParameters[parameterName] = ""

                    # Iterate through all accepted parameters and add them to a single string
                    for acceptedParameter in parameterObject.getAcceptedParameters():
                        acceptedObject = parameterObject.getAcceptedParameters()[acceptedParameter]
                        
                        # Add parameter info to string
                        acceptedParameters[parameterName] += "`{}` - {}\n".format(
                            " | ".join(acceptedObject.getAlternatives()),
                            acceptedObject.getInfo()
                        )
            
            # Add Accepted Parameter Fields
            for param in acceptedParameters:

                # Setup fields
                fields = []
                fieldText = ""
                acceptedParams = acceptedParameters[param].split("\n")

                for parameter in acceptedParams:
                    
                    accepted = censor(parameter) if not isNSFW else parameter
                    accepted += "\n"

                    if len(fieldText) + len(accepted) >= OmegaPsi.MESSAGE_THRESHOLD:
                        fields.append(fieldText)
                        fieldText = ""
                    
                    fieldText += accepted
                
                if len(fieldText) > 0:
                    fields.append(fieldText)
                
                # Add fields to accepted parameters
                count = 0
                for field in fields:
                    count += 1
                    embed.add_field(
                        name = "{} Parameters {}".format(
                            param,
                            "({} / {})".format(
                                count, len(fields)
                            ) if len(fields) > 1 else ""
                        ),
                        value = field,
                        inline = False
                    )
            
            return embed
        
        # Not inDepth
        else:

            # Setup Placeholder Parameters Text
            placeholderParameters = []
            for parameter in self.getParameters():
                placeholderParameters.append("{}{}{}".format(
                    "[" if self.getParameters()[parameter].isOptional() else "<",
                    parameter,
                    "]" if self.getParameters()[parameter].isOptional() else ">"
                ))
            placeholders = " ".join(placeholderParameters)

            return (
                "`{} {}` - {}\n".format(
                    censor(self.getAlternatives()[0], True) if not isNSFW else self.getAlternatives()[0],
                    censor(placeholders) if not isNSFW else placeholders,
                    censor(self.getInfo()) if not isNSFW else self.getInfo()
                )
            )
    
    def getHTML(self):
        """Returns the HTML render text for the Command.\n
        """

        # Setup HTML Text
        html = ""

        # Add Commands and Placeholder Parameters
        placeholderParameters = []
        for parameter in self.getParameters():
            placeholderParameters.append("{}{}{}".format(
                "[" if self.getParameters()[parameter].isOptional() else "&lt;",
                parameter,
                "]" if self.getParameters()[parameter].isOptional() else "&gt;"
            ))
        
        html += (
            "       <tr>\n" +
            "           <td id=\"commandBorder\" style=\"width: 185px; text-align: left;\">{}</td>\n" +
            "           <td id=\"commandBorder\" style=\"width: 185px; text-align: left;\">{}</td>\n" +
            "           <td id=\"commandBorder\" style=\"width: 185px; text-align: left;\">{}</td>\n" +
            "       </tr>\n"
        ).format(
            ", ".join(self.getAlternatives()),
            " ".join(placeholderParameters) if len(placeholderParameters) > 0 else "None",
            self.getInfo()
        )

       # Setup Accepted Parameter Fields
        for parameter in self.getParameters():
            parameterName = parameter
            parameterObject = self.getParameters()[parameter]

            # Only add if there are accepted parameters
            if len(parameterObject.getAcceptedParameters()) > 0:
                html += (
                    "    <tr>\n" +
                    "        <td id=\"noBorder\" style=\"width: 185px; text-align: left;\"><em></em></td>\n" +
                    "        <td id=\"acceptedBorder\" style=\"width: 185px; text-align: left;\"><em><strong>{}</strong></em></td>\n" +
                    "        <td id=\"acceptedBorder\"style=\"width: 185px; text-align: left;\"><em><strong>{}</strong></em></td>\n" +
                    "    </tr>\n"
                ).format(
                    "Accepted Parameters For " + parameterName,
                    parameterObject.getInfo()
                )

                # Iterate through all accepted parameters and add them to a single string
                for acceptedParameter in parameterObject.getAcceptedParameters():
                    acceptedObject = parameterObject.getAcceptedParameters()[acceptedParameter]
                    html += (
                        "    <tr>\n" +
                        "        <td id=\"noBorder\" style=\"width: 185px; text-align: left;\"><em></em></td>\n" +
                        "        <td id=\"acceptedBorder\" style=\"width: 185px; text-align: left;\"><em>{}</em></td>\n" +
                        "        <td id=\"acceptedBorder\" style=\"width: 185px; text-align: left;\"><em>{}</em></td>\n" +
                        "    </tr>\n"
                    ).format(
                        " | ".join(acceptedObject.getAlternatives()),
                        acceptedObject.getInfo()
                    )
        
        return html
    
    def getMarkdown(self):
        """Returns the markdown render text for the Command.\n
        """

        # Setup markdown Text
        markdown = ""

        # Add Commands and Placeholder Parameters
        placeholderParameters = []
        for parameter in self.getParameters():
            placeholderParameters.append("{}{}{}".format(
                "[" if self.getParameters()[parameter].isOptional() else "<",
                parameter,
                "]" if self.getParameters()[parameter].isOptional() else ">"
            ))
        
        markdown += ("  * `{} {}` - {}\n").format(
            " | ".join(self.getAlternatives()),
            " ".join(placeholderParameters) if len(placeholderParameters) > 0 else "",
            self.getInfo()
        )

       # Setup Accepted Parameter Fields
        for parameter in self.getParameters():
            parameterName = parameter
            parameterObject = self.getParameters()[parameter]

            # Only add if there are accepted parameters
            if len(parameterObject.getAcceptedParameters()) > 0:
                markdown += ("    * {}\n").format(
                    "Accepted Parameters For " + parameterName
                )

                # Iterate through all accepted parameters and add them to a single string
                for acceptedParameter in parameterObject.getAcceptedParameters():
                    acceptedObject = parameterObject.getAcceptedParameters()[acceptedParameter]
                    markdown += ("      * `{}` - {}\n").format(
                        " | ".join(acceptedObject.getAlternatives()),
                        acceptedObject.getInfo()
                    )
        
        return markdown

# Timeout Decorator
class TimeoutError(Exception): pass
def timeout(seconds = 10, error_message = "Function timed out"):
    def decorator(func):
        def _handle_timeout(signum, frame):
            return discord.Embed(
                title = "Error",
                description = error_message,
                colour = 0xFF0000
            )
        
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            except:
                result = error_message
            finally:
                signal.alarm(0)
            return result
        
        return wraps(func)(wrapper)
    
    return decorator
