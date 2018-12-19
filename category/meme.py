from util.file.database import loop
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server

from util.meme import areYouAwake
from util.meme import bikeCrash
from util.meme import brainOf
from util.meme import burnLetter
from util.meme import butILikeThis
from util.meme import carSkidding
from util.meme import cardSlam
from util.meme import classroomStares
from util.meme import deerAboveWater
from util.meme import didYouMean
from util.meme import executiveOrder
from util.meme import expandingBrain
from util.meme import fearNot
from util.meme import flexSeal
from util.meme import gangUp
from util.meme import grusPlan
from util.meme import headacheTypes
from util.meme import holdUpEarth
from util.meme import iCantRead
from util.meme import icarlyStopSign
from util.meme import kevinHitDwight
from util.meme import mastersBlessing
from util.meme import nArmHandshake
from util.meme import pigeon
from util.meme import playstation
from util.meme import puppetMeme
from util.meme import rewindTime
from util.meme import runAway
from util.meme import saveOne
from util.meme import sayItAgain
from util.meme import soccerTongue
from util.meme import spontaneousAnger
from util.meme import startLearning
from util.meme import surprisedDwight
from util.meme import surprisedPikachu
from util.meme import thanosStone
from util.meme import threeDoors
from util.meme import trojanHorse
from util.meme import trump
from util.meme import whoKilledHannibal

from util.utils.discordUtils import sendMessage, getErrorMessage, didAuthorVote

from functools import partial
from random import choice as choose
from supercog import Category, Command
import discord, os, requests

class Meme(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    MEME_SUBREDDITS = [
        "meme",
        "memes",
        "dankmeme",
        "dank_meme"
    ]
    MEME_RANDOM = "https://www.reddit.com/r/{}/.json?sort=top&limit=500"

    REDDIT_BASE = "https://www.reddit.com"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    NO_IMAGE = "NO_IMAGE"

    MISSING_PARAMETER = "MISSING_PARAMETER"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client,
            "Meme",
            description = "Memes, memes, and more memes.",
            embed_color = 0xD1FF9E,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self._meme = Command(commandDict = {
            "alternatives": ["meme"],
            "info": "Sends a random meme from Reddit.",
            "errors": {
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a meme, you don't need any parameters."
                    ]
                },
                Meme.NO_IMAGE: {
                    "messages": [
                        "Somehow there were no memes found??? Idk try again."
                    ]
                }
            },
            "command": self.meme
        })

        self._areYouAwake = Command(commandDict = {
            "alternatives": ["areYouAwake"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": areYouAwake.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "text": {
                    "info": "The text that goes inside the speech bubble for the brain.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need a single set of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need a single set of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.areYouAwake
        })

        self._bikeCrash = Command(commandDict = {
            "alternatives": ["bikeCrash"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": bikeCrash.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "firstText": {
                    "info": "The text that goes where the bike riders are normally driving.",
                    "optional": False
                },
                "crashText": {
                    "info": "The text that goes where the riders crash.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.bikeCrash
        })

        self._brainOf = Command(commandDict = {
            "alternatives": ["brainOf"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": brainOf.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "text": {
                    "info": "The text that goes on the last brain image.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need text."
                    ]
                }
            },
            "command": self.brainOf
        })

        self._burnLetter = Command(commandDict = {
            "alternatives": ["burnLetter"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": burnLetter.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "letterText": {
                    "info": "The text that goes on the piece of paper.",
                    "optional": False
                },
                "spongebobText": {
                    "info": "The text that goes on spongebob.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.burnLetter
        })

        self._butILikeThis = Command(commandDict = {
            "alternatives": ["butILikeThis", "thisIsBetter"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": butILikeThis.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "redCarText": {
                    "info": "The text to put on the red car.",
                    "optional": False
                },
                "whiteCarText": {
                    "info": "The text to put on the white car.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.butILikeThis
        })

        self._carSkidding = Command(commandDict = {
            "alternatives": ["carSkidding", "carSkid"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": carSkidding.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "carText": {
                    "info": "The text to put on the car.",
                    "optional": False
                },
                "straightText": {
                    "info": "The text to put on the straight ahead part of the sign.",
                    "optional": False
                },
                "exitText": {
                    "info": "The text to put on the exit part of the sign.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To generate this meme, you need to give at least 3 sets of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters for this. You only need 3 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.carSkidding
        })

        self._cardSlam = Command(commandDict = {
            "alternatives": ["cardSlam"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": cardSlam.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "cardText": {
                    "info": "The text to put on top of the card.",
                    "optional": False
                },
                "bodyText": {
                    "info": "The text to put on top of the man.",
                    "optional": False
                },
                "tableText": {
                    "info": "The text to put on top of the table.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 3 sets of text each wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text each wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.cardSlam
        })

        self._classroomStares = Command(commandDict = {
            "alternatives": ["classroomStares"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": classroomStares.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "bubbleText": {
                    "info": "The text that shows up on the bubble quote.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need the bubble text to generate this meme."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need the bubble text to generate this meme."
                    ]
                }
            },
            "command": self.classroomStares
        })

        self._deerAboveWater = Command(commandDict = {
            "alternatives": ["deerAboveWater", "deerAbove"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": deerAboveWater.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "deerText": {
                    "info": "The text that goes on top of the deer.",
                    "optional": False
                },
                "handText": {
                    "info": "The text that goes on top of the arm.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need at least 2 parameters to generate this meme."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need 2 parameters to generate this meme."
                    ]
                }
            },
            "command": self.deerAboveWater
        })

        self._didYouMean = Command(commandDict = {
            "alternatives": ["didYouMean"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": didYouMean.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "searchText": {
                    "info": "The text that goes in the search bar.",
                    "optional": True
                },
                "didYouMeanText": {
                    "info": "The text that goes where it says *Did You Mean*",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need at least 1 parameter to generate this meme."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need 2 parameters to generate this meme."
                    ]
                }
            },
            "command": self.didYouMean
        })

        self._executiveOrder = Command(commandDict = {
            "alternatives": ["executiveOrder", "execOrder"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": executiveOrder.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "text": {
                    "info": "The text that goes on top of the executive order.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need text to send to the executive order."
                    ]
                }
            },
            "command": self.executiveOrder
        })

        self._expandingBrain = Command(commandDict = {
            "alternatives": ["expandingBrain", "expBrain"],
            "info": {
                "text": "Sends a generated meme based off {} image.",
                "hyperlink": expandingBrain.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "firstText": {
                    "info": "The text to put in the first box.",
                    "optional": False
                },
                "secondText": {
                    "info": "The text to put in the second box.",
                    "optional": True
                },
                "thirdText": {
                    "info": "The text to put in the third box.",
                    "optional": True
                },
                "fourthText": {
                    "info": "The text to put in the fourth box.",
                    "optional": True
                },
                "fifthText": {
                    "info": "The text to put in the fifth box.",
                    "optional": True
                },
                "sixthText": {
                    "info": "The text to put in the sixth box.",
                    "optional": True
                },
                "seventhText": {
                    "info": "The text to put in the seventh box.",
                    "optional": True
                },
                "eighthText": {
                    "info": "The text to put in the eighth box.",
                    "optional": True
                },
                "ninthText": {
                    "info": "The text to put in the ninth box.",
                    "optional": True
                },
                "tenthText": {
                    "info": "The text to put in the tenth box.",
                    "optional": True
                },
                "eleventhText": {
                    "info": "The text to put in the eleventh box.",
                    "optional": True
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least a single set of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you can have a maximum of 11 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.expandingBrain
        })

        self._fearNot = Command(commandDict = {
            "alternatives": ["fearNot"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": fearNot.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "speechText": {
                    "info": "The text that goes in the speech bubble of the woman.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to run this, you need the text that will go in the speech bubble."
                    ]
                }
            },
            "command": self.fearNot
        })

        self._flexSeal = Command(commandDict = {
            "alternatives": ["flexSeal"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": flexSeal.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "holderText": {
                    "info": "The text that goes on top of the person holding the box.",
                    "optional": False
                },
                "boxText": {
                    "info": "The text that goes on top of the box.",
                    "optional": False
                },
                "receiverText": {
                    "info": "The text that goes on top of the receiver.",
                    "optional": False
                }
            },
            "command": self.flexSeal
        })

        self._gangUp = Command(commandDict = {
            "alternatives": ["gangUp"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": gangUp.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "attackerOne": {
                    "info": "The text that goes on top of the first attacker.",
                    "optional": False
                },
                "attackerTwo": {
                    "info": "The text that goes on top of the second attacker.",
                    "optional": False
                },
                "attackerThree": {
                    "info": "The text that goes on top of the third attacker.",
                    "optional": False
                },
                "bodySlamAttacker": {
                    "info": "The text that goes on top of the attacker who body slams the person.",
                    "optional": False
                },
                "personText": {
                    "info": "The text that goes on top of the person.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 5 sets of text wrapped in quotes (\")"
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 5 sets of text wrapped in quotes (\")"
                    ]
                }
            },
            "command": self.gangUp
        })

        self._grusPlan = Command(commandDict = {
            "alternatives": ["grusPlan"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": grusPlan.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "firstPanelText": {
                    "info": "The text that goes on the first panel.",
                    "optional": False
                },
                "secondPanelText": {
                    "info": "The text that goes on the second panel.",
                    "optional": False
                },
                "lastPanelText": {
                    "info": "The text that goes on the last panels.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 3 sets of text wrapped in quotes (\")"
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text wrapped in quotes (\")"
                    ]
                }
            },
            "command": self.grusPlan
        })

        self._headacheTypes = Command(commandDict = {
            "alternatives": ["headacheTypes", "headache"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": headacheTypes.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "text": {
                    "info": "The text that goes above the last headache.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need the text in order to generate this meme."
                    ]
                }
            },
            "command": self.headacheTypes
        })

        self._holdUpEarth = Command(commandDict = {
            "alternatives": ["holdUpEarth", "holdUp"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": holdUpEarth.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "earthText": {
                    "info": "The text that goes on top of Earth.",
                    "optional": False
                },
                "personText": {
                    "info": "The text that goes on top of the person holding up the Earth.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 2 sets of text wrapped in quotes (\")"
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")"
                    ]
                }
            },
            "command": self.holdUpEarth
        })

        self._iCantRead = Command(commandDict = {
            "alternatives": ["iCantRead", "cantRead"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": iCantRead.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "signText": {
                    "info": "The text that goes on top of the sign.",
                    "optional": False
                },
                "personText": {
                    "info": "The text that goes on top of the person.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 2 sets of text wrapped in quotes (\")"
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")"
                    ]
                }
            },
            "command": self.iCantRead
        })

        self._icarlyStopSign = Command(commandDict = {
            "alternatives": ["icarlyStopSign", "icarlyStop"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": icarlyStopSign.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "spencerText": {
                    "info": "The text that goes on top of Spencer.",
                    "optional": False
                },
                "stopText": {
                    "info": "The text that goes on top of the stop sign.",
                    "optional": True
                },
                "gibbyText": {
                    "info":"The text that goes on top of Gibby.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need 3 parameters to generate this meme."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need 3 different sets of text to put on the meme."
                    ]
                }
            },
            "command": self.icarlyStopSign
        })

        self._kevinHitDwight = Command(commandDict = {
            "alternatives": ["kevinHitDwight", "kevinDwight", "kevinPan"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": kevinHitDwight.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "kevinText": {
                    "info": "The text that goes on top of Kevin.",
                    "optional": False
                },
                "dwightText": {
                    "info": "The text that goes on top of Dwight.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")"
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")"
                    ]
                }
            },
            "command": self.kevinHitDwight
        })

        self._mastersBlessing = Command(commandDict = {
            "alternatives": ["mastersBlessing"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": mastersBlessing.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "masterText": {
                    "info": "The text that goes on top of the master.",
                    "optional": False
                },
                "swordText": {
                    "info": "The text that goes on top of the sword.",
                    "optional": False
                },
                "apprenticeText": {
                    "info": "The text that goes on top of the apprentice.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 3 sets of text each wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text each wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.mastersBlessing
        })

        self._nArmHandshake = Command(commandDict = {
            "alternatives": ["armHandshake"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": nArmHandshake.IMAGE_TWO,
                "hyperlink_text": "this"
            },
            "parameters": {
                "handsText": {
                    "info": "The text that goes on the joined hands.",
                    "optional": False
                },
                "firstArm": {
                    "info": "The text that goes on the first arm.",
                    "optional": False
                },
                "secondArm": {
                    "info": "The text that goes on the second arm.",
                    "optional": False
                },
                "thirdArm": {
                    "info": "The text that goes on the third arm.",
                    "optional": True
                },
                "fourthArm": {
                    "info": "The text that goes on the fourth arm.",
                    "optional": True
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 3 sets of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you can have up to 5 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "commands": self.nArmHandshake
        })

        self._pigeon = Command(commandDict = {
            "alternatives": ["pigeon", "isThisAPigeon"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": pigeon.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "pigeonText": {
                    "info": "The text that goes over top of the pigeon.",
                    "optional": False
                },
                "personText": {
                    "info": "The text that goes over top of the person.",
                    "optional": False
                },
                "questionText": {
                    "info": "The text that asks a question.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 3 sets of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.pigeon
        })

        self._playstation = Command(commandDict = {
            "alternatives": ["playstation"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": playstation.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "triangleText": {
                    "info": "The text that goes next to the triangle button.",
                    "optional": True
                },
                "squareText": {
                    "info": "The text that goes next to the square button.",
                    "optional": True
                },
                "xText": {
                    "info": "The text that goes next to the X button.",
                    "optional": False
                },
                "circleText": {
                    "info": "The text that goes next to the circle button.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you can have a maximum of 4 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.playstation
        })

        self._puppetMeme = Command(commandDict = {
            "alternatives": ["puppetMeme"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": puppetMeme.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "handText": {
                    "info": "The text that goes on the puppeteers hand.",
                    "optional": False
                },
                "puppetText": {
                    "info": "The text that goes on top of the puppet.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.puppetMeme
        })

        self._rewindTime = Command(commandDict = {
            "alternatives": ["rewindTime"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": rewindTime.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "text": {
                    "info": "The text that goes at the top of the meme.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need some text to generate this meme."
                    ]
                }
            },
            "command": self.rewindTime
        })

        self._runAway = Command(commandDict = {
            "alternatives": ["runAway"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": runAway.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "chaserText": {
                    "info": "The text that goes on top of the chaser.",
                    "optional": False  
                },
                "runnerText": {
                    "info": "The text that goes on top of the runner.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.runAway
        })

        self._saveOne = Command(commandDict = {
            "alternatives": ["saveOne"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": saveOne.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "personText": {
                    "info": "The text that goes on top of the person.",
                    "optional": False
                },
                "leftBehindText": {
                    "info": "The text that goes on top of the person that is left behind.",
                    "optional": False
                },
                "savedText": {
                    "info": "The text that goes on top of the person who is being saved.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 3 sets of text each wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text each wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.saveOne
        })

        self._sayItAgain = Command(commandDict = {
            "alternatives": ["sayItAgain", "dexterMeme"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": sayItAgain.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "topText": {
                    "info": "The text that goes on the top part of the image.",
                    "optional": False
                },
                "bottomText": {
                    "info": "The text that goes on the bottom part of the image.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 2 sets of text each wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text each wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.sayItAgain
        })

        self._soccerTongue = Command(commandDict = {
            "alternatives": ["soccerTongue", "soccer"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": soccerTongue.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "tongueText": {
                    "info": "The text that goes on top of the guy sticking his tongue out.",
                    "optional": False
                },
                "personText": {
                    "info": "The text that goes on top of the guy in front of the tongue guy.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")"
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")"
                    ]
                }
            },
            "command": self.soccerTongue
        })

        self._spontaneousAnger = Command(commandDict = {
            "alternatives": ["spontaneousAnger", "angerMeme"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": spontaneousAnger.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "angerText": {
                    "info": "The text that goes above the guy who gets angry.",
                    "optional": False
                },
                "questionText": {
                    "info": "The text that goes above the guy who questions the angry guy.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 2 sets of text each wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text each wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.spontaneousAnger
        })

        self._startLearning = Command(commandDict = {
            "alternatives": ["startLearning", "learnLanguage"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": startLearning.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "topText": {
                    "info": "The text that goes on top of the meme.",
                    "optional": False
                },
                "insteadOfOne": {
                    "info": "The text that goes in the first Instead Of box.",
                    "optional": False
                },
                "sayOne": {
                    "info": "The text that goes in the first Say box.",
                    "optional": False
                },
                "insteadOfTwo": {
                    "info": "The text that goes in the second Instead Of box.",
                    "optional": True
                },
                "sayTwo": {
                    "info": "The text that goes in the second Say box.",
                    "optional": True
                },
                "insteadOfThree": {
                    "info": "The text that goes in the third Instead Of box.",
                    "optional": True
                },
                "sayThree": {
                    "info": "The text that goes in the third Say box.",
                    "optional": True
                },
                "insteadOfFour": {
                    "info": "The text that goes in the fourth Instead Of box.",
                    "optional": True
                },
                "sayFour": {
                    "info": "The text that goes in the fourth Say box.",
                    "optional": True
                },
                "insteadOfFive": {
                    "info": "The text that goes in the five Instead Of box.",
                    "optional": True
                },
                "sayFive": {
                    "info": "The text that goes in the five Say box.",
                    "optional": True
                },
                "insteadOfSix": {
                    "info": "The text that goes in the six Instead Of box.",
                    "optional": True
                },
                "saySix": {
                    "info": "The text that goes in the six Say box.",
                    "optional": True
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 3 sets of text wrapped in quotes (\")"
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you can have a maximum of 13 sets of text wrapped in quotes (\")"
                    ]
                },
                Meme.MISSING_PARAMETER: {
                    "messages": [
                        "To generate this meme, you need a pair of \"instead of, say\" texts. You're missing one."
                    ]
                }
            },
            "command": self.startLearning
        })

        self._surprisedDwight = Command(commandDict = {
            "alternatives": ["surprisedDwight"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": surprisedDwight.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "dwightText": {
                    "info": "The text that goes above Dwight.",
                    "optional": False
                },
                "angelaText": {
                    "info": "The text that goes above Angela.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 2 sets of text each wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text each wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.surprisedDwight
        })

        self._surprisedPikachu = Command(commandDict = {
            "alternatives": ["surprisedPikachu"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": surprisedPikachu.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "firstLine": {
                    "info": "The first line to put on the meme.",
                    "optional": False
                },
                "secondLine": {
                    "info": "The second line to put on the meme.",
                    "optional": False
                },
                "thirdLine": {
                    "info": "The third line to put on the meme.",
                    "optional": False
                },
                "fourthLine": {
                    "info": "The fourth line to put on the meme.",
                    "optional": True
                },
                "fifthLine": {
                    "info": "The fifth line to put on the meme.",
                    "optional": True
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 3 lines to add."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "There is a maximum of 5 lines you can put on this meme."
                    ]
                }
            },
            "command": self.surprisedPikachu
        })

        self._thanosStone = Command(commandDict = {
            "alternatives": ["thanosStone"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": thanosStone.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "stoneText": {
                    "info": "The text that goes above where Thanos puts in the mind stone.",
                    "optional": False
                },
                "thanosText": {
                    "info": "The text that goes where Thanos is feeling the charge of all the stones.",
                    "optional": False
                }
            },
            "command": self.thanosStone
        })

        self._threeDoors = Command(commandDict = {
            "alternatives": ["threeDoors"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": threeDoors.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "firstDoorText": {
                    "info": "The text that goes above the first door.",
                    "optional": False
                },
                "secondDoorText": {
                    "info": "The text that goes above the first door.",
                    "optional": False
                },
                "thirdDoorText": {
                    "info": "The text that goes above the first door.",
                    "optional": False
                },
                "personText": {
                    "info": "The text that goes on top of the person.",
                    "optional": True
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 3 sets of text wrapped in quotes (\")"
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text wrapped in quotes (\")"
                    ]
                }
            },
            "command": self.threeDoors
        })

        self._trojanHorse = Command(commandDict = {
            "alternatives": ["trojanHorse"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": trojanHorse.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "hidersText": {
                    "info": "The text that goes on top of the hiders in the horse.",
                    "optional": False
                },
                "horseText": {
                    "info": "The text that goes on top of the horse head.",
                    "optional": False
                },
                "castleText": {
                    "info": "The text that goes on top of the castle.",
                    "optional": False
                },
                "welcomersText": {
                    "info": "The text that goes on top of the welcomers.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 4 sets of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 4 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.trojanHorse
        })

        self._trump = Command(commandDict = {
            "alternatives": ["trump", "trumpTweet"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": trump.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "tweetText": {
                    "info": "The text that goes inside the tweet.",
                    "optional": False
                }
            },
            "command": self.trump
        })

        self._whoKilledHannibal = Command(commandDict = {
            "alternatives": ["whoKilledHannibal"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": whoKilledHannibal.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "ericAndreText": {
                    "info": "The text that goes on top of Eric Andre.",
                    "optional": False
                },
                "gunText": {
                    "info": "The text that goes on top of the gun.",
                    "optional": False
                },
                "hannibalText": {
                    "info": "The text that goes on top of Hannibal.",
                    "optional": False
                },
                "questionText": {
                    "info": "The text that goes as the question text.",
                    "optional": False
                }
            },
            "errors": {
                Meme.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 4 sets of text wrapped in quotes (\")."
                    ]
                },
                Meme.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 4 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.whoKilledHannibal
        })  

        self.setCommands([
            self._meme,
            self._areYouAwake,
            self._bikeCrash,
            self._brainOf,
            self._burnLetter,
            self._butILikeThis,
            self._carSkidding,
            self._cardSlam,
            self._classroomStares,
            self._deerAboveWater,
            self._didYouMean,
            self._executiveOrder,
            self._expandingBrain,
            self._fearNot,
            self._flexSeal,
            self._gangUp,
            self._grusPlan,
            self._headacheTypes,
            self._holdUpEarth,
            self._iCantRead,
            self._icarlyStopSign,
            self._kevinHitDwight,
            self._mastersBlessing,
            self._nArmHandshake,
            self._pigeon,
            self._playstation,
            self._puppetMeme,
            self._rewindTime,
            self._runAway,
            self._saveOne,
            self._sayItAgain,
            self._soccerTongue,
            self._spontaneousAnger,
            self._startLearning,
            self._surprisedDwight,
            self._surprisedPikachu,
            self._thanosStone,
            self._threeDoors,
            self._trojanHorse,
            self._trump,
            self._whoKilledHannibal
        ]) 
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def meme(self, message, parameters):
        """Returns a random meme from Reddit.\n

        Parameters:
            channel (discord.Channel): The channel to send to. Helps to determine NSFW memes
        """

        # See if channel has is_nsfw
        try:
            isNSFW = message.channel.is_nsfw()
        
        # Channel is private, allow NSFW
        except:
            isNSFW = True

        # Get data involving Reddit memes
        # Choose random subreddit between meme subreddits (meme, memes, dankmemes, dank_meme)
        subreddit = choose(Meme.MEME_SUBREDDITS)

        redditData = await loop.run_in_executor(None,
            partial(
                requests.get,
                Meme.MEME_RANDOM.format(subreddit),
                headers = {
                    "User-agent": "Omega Psi"
                }
            )
        )
        redditData = redditData.json()

        # Make sure there are reddit posts
        if len(redditData["data"]["children"]) == 0:
            embed = getErrorMessage(self._meme, Meme.NO_IMAGE)
        
        # There were reddit posts
        else:

            # Choose random reddit post
            redditPost = choose(redditData["data"]["children"])["data"]
            while redditPost["is_video"] or (redditPost["over_18"] and not isNSFW):
                redditPost = choose(redditData["data"]["children"])["data"]

            # Return an embed for the reddit post
            embed = discord.Embed(
                name = "Meme Result",
                description = "[{}]({})".format(
                    redditPost["title"],
                    Meme.REDDIT_BASE + redditPost["permalink"]
                ),
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            ).set_image(
                url = redditPost["url"]
            ).set_footer(
                text = "👍 {} 💬 {}".format(
                    redditPost["score"],
                    redditPost["num_comments"]
                )
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
    
    async def areYouAwake(self, message, parameters):
        """Generates and sends the Are You Awake meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._areYouAwake.getMinParameters():
            result = getErrorMessage(self._areYouAwake, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._areYouAwake.getMaxParameters():
            result = getErrorMessage(self._areYouAwake, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                areYouAwake.generateImage,
                parameters[0]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def bikeCrash(self, message, parameters):
        """Generates and sends the Bike Crash meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._bikeCrash.getMinParameters():
            result = getErrorMessage(self._bikeCrash, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._bikeCrash.getMaxParameters():
            result = getErrorMessage(self._bikeCrash, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                bikeCrash.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
        
    async def brainOf(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._brainOf.getMinParameters():
            result = getErrorMessage(self._brainOf, Meme.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                brainOf.generateImage,
                " ".join(parameters)
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def burnLetter(self, message, parameters):
        """Generates and sends the Burn Letter meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._burnLetter.getMinParameters():
            result = getErrorMessage(self._burnLetter, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._burnLetter.getMaxParameters():
            result = getErrorMessage(self._burnLetter, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                burnLetter.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def butILikeThis(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._butILikeThis.getMinParameters():
            result = getErrorMessage(self._butILikeThis, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._butILikeThis.getMaxParameters():
            result = getErrorMessage(self._butILikeThis, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                butILikeThis.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def carSkidding(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._carSkidding.getMinParameters():
            result = getErrorMessage(self._carSkidding, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._carSkidding.getMaxParameters():
            result = getErrorMessage(self._carSkidding, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                carSkidding.generateImage,
                parameters[0],
                parameters[1],
                parameters[2]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def cardSlam(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._cardSlam.getMinParameters():
            result = getErrorMessage(self._cardSlam, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._cardSlam.getMaxParameters():
            result = getErrorMessage(self._cardSlam, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                cardSlam.generateImage,
                parameters[0],
                parameters[1],
                parameters[2]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def classroomStares(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._classroomStares.getMinParameters():
            result = getErrorMessage(self._classroomStares, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._classroomStares.getMaxParameters():
            result = getErrorMessage(self._classroomStares, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                classroomStares.generateImage,
                parameters[0]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def deerAboveWater(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._deerAboveWater.getMinParameters():
            result = getErrorMessage(self._deerAboveWater, Meme.NOT_ENOUGH_PARAMETERS)

        # Check for too many parameters
        elif len(parameters) > self._deerAboveWater.getMaxParameters():
            result = getErrorMessage(self._deerAboveWater, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                deerAboveWater.generateImage,
                parameters[0],
                parameters[1]
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def didYouMean(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._didYouMean.getMinParameters():
            result = getErrorMessage(self._didYouMean, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._didYouMean.getMaxParameters():
            result = getErrorMessage(self._didYouMean, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Check if only 1 parameter (only generate Did You Mean part)
            if len(parameters) == 1:
                result = await loop.run_in_executor(None,
                    didYouMean.generateImage,
                    "",
                    parameters[0]
                )
            
            else:
                result = await loop.run_in_executor(None,
                    didYouMean.generateImage,
                    parameters[0],
                    parameters[1]
                )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def executiveOrder(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._executiveOrder.getMinParameters():
            result = getErrorMessage(self._executiveOrder, Meme.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                executiveOrder.generateImage,
                " ".join(parameters)
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def expandingBrain(self, message, parameters):
        """Generates and sends the brain size meme.
        """

        # Check if user voted for bot on discordbots.org
        if await didAuthorVote(message.author):

            # Check for not enough parameters
            if len(parameters) < self._expandingBrain.getMinParameters():
                result = getErrorMessage(self._expandingBrain, Meme.NOT_ENOUGH_PARAMETERS)
            
            # Check for too many parameters
            elif len(parameters) > self._expandingBrain.getMaxParameters():
                result = getErrorMessage(self._expandingBrain, Meme.TOO_MANY_PARAMETERS)
            
            # There were the proper amount of parameters
            else:
                result = await loop.run_in_executor(None,
                    expandingBrain.generateImage,
                    parameters
                )
            
            # Check if an error was made
            if type(result) == discord.Embed:
                await sendMessage(
                    self.client,
                    message,
                    embed = result
                )
            
            # No error was made, send image
            else:

                # Send message then remove image
                await sendMessage(
                    self.client,
                    message,
                    filename = result
                )

                os.remove(result)
        
        # Author did not vote
        else:
            embed = discord.Embed(
                title = "Vote!",
                description = "To run this command, you must [vote](https://discordbots.org/bot/503804826187071501/vote) for Omega Psi.",
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )

            await sendMessage(
                self.client,
                message,
                embed = embed
            )
    
    async def fearNot(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._fearNot.getMinParameters():
            result = getErrorMessage(self._fearNot, Meme.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                fearNot.generateImage,
                " ".join(parameters)
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def flexSeal(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._flexSeal.getMinParameters():
            result = getErrorMessage(self._flexSeal, Meme.NOT_ENOUGH_PARAMETERS)

        # Check for too many parameters
        elif len(parameters) > self._flexSeal.getMaxParameters():
            result = getErrorMessage(self._flexSeal, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                flexSeal.generateImage,
                parameters[0],
                parameters[1],
                parameters[2]
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def gangUp(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._gangUp.getMinParameters():
            result = getErrorMessage(self._gangUp, Meme.NOT_ENOUGH_PARAMETERS)

        # Check for too many parameters
        elif len(parameters) > self._gangUp.getMaxParameters():
            result = getErrorMessage(self._gangUp, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                gangUp.generateImage,
                parameters[0],
                parameters[1],
                parameters[2],
                parameters[3],
                parameters[4]
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def grusPlan(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._grusPlan.getMinParameters():
            result = getErrorMessage(self._grusPlan, Meme.NOT_ENOUGH_PARAMETERS)

        # Check for too many parameters
        elif len(parameters) > self._grusPlan.getMaxParameters():
            result = getErrorMessage(self._grusPlan, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                grusPlan.generateImage,
                parameters[0],
                parameters[1],
                parameters[2]
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def headacheTypes(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._headacheTypes.getMinParameters():
            result = getErrorMessage(self._headacheTypes, Meme.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                headacheTypes.generateImage,
                " ".join(parameters)
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def holdUpEarth(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._holdUpEarth.getMinParameters():
            result = getErrorMessage(self._holdUpEarth, Meme.NOT_ENOUGH_PARAMETERS)

        # Check for too many parameters
        elif len(parameters) > self._holdUpEarth.getMaxParameters():
            result = getErrorMessage(self._holdUpEarth, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                holdUpEarth.generateImage,
                parameters[0],
                parameters[1]
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def iCantRead(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._iCantRead.getMinParameters():
            result = getErrorMessage(self._iCantRead, Meme.NOT_ENOUGH_PARAMETERS)

        # Check for too many parameters
        elif len(parameters) > self._iCantRead.getMaxParameters():
            result = getErrorMessage(self._iCantRead, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                iCantRead.generateImage,
                parameters[0],
                parameters[1]
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def icarlyStopSign(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._icarlyStopSign.getMinParameters():
            result = getErrorMessage(self._icarlyStopSign, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._icarlyStopSign.getMaxParameters():
            result = getErrorMessage(self._icarlyStopSign, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            
            # Check if there are only 2 parameters
            if len(parameters) == 2:
                result = await loop.run_in_executor(None,
                    icarlyStopSign.generateImage,
                    parameters[0],
                    "",
                    parameters[1]
                )
            else:
                result = await loop.run_in_executor(None,
                    icarlyStopSign.generateImage,
                    parameters[0],
                    parameters[1],
                    parameters[2]
                )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def kevinHitDwight(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._kevinHitDwight.getMinParameters():
            result = getErrorMessage(self._kevinHitDwight, Meme.NOT_ENOUGH_PARAMETERS)

        # Check for too many parameters
        elif len(parameters) > self._kevinHitDwight.getMaxParameters():
            result = getErrorMessage(self._kevinHitDwight, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                kevinHitDwight.generateImage,
                parameters[0],
                parameters[1]
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def mastersBlessing(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._mastersBlessing.getMinParameters():
            result = getErrorMessage(self._mastersBlessing, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._mastersBlessing.getMaxParameters():
            result = getErrorMessage(self._mastersBlessing, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                mastersBlessing.generateImage,
                parameters[0],
                parameters[1],
                parameters[2]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def nArmHandshake(self, message, parameters):
        """
        """

        # Check if author voted on discordbots.org
        if await didAuthorVote(message.author):
        
            # Check for not enough parameters
            if len(parameters) < self._nArmHandshake.getMinParameters():
                result = getErrorMessage(self._nArmHandshake, Meme.NOT_ENOUGH_PARAMETERS)
            
            # Check for too many parameters
            elif len(parameters) > self._nArmHandshake.getMaxParameters():
                result = getErrorMessage(self._nArmHandshake, Meme.TOO_MANY_PARAMETERS)
            
            # There were the proper amount of parameters
            else:
                result = await loop.run_in_executor(None,
                    nArmHandshake.generateImage,
                    parameters[0],
                    parameters[1],
                    parameters[2],
                    "" if len(parameters) < 4 else parameters[3],
                    "" if len(parameters) < 5 else parameters[4]
                )

            # Check if an error was made
            if type(result) == discord.Embed:
                await sendMessage(
                    self.client,
                    message,
                    embed = result
                )
            
            # No error was made, send image
            else:

                # Send message then remove image
                await sendMessage(
                    self.client,
                    message,
                    filename = result
                )

                os.remove(result)
        
        # Author did not vote
        else:
            embed = discord.Embed(
                title = "Vote!",
                description = "To run this command, you must [vote](https://discordbots.org/bot/503804826187071501/vote) for Omega Psi.",
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )

            await sendMessage(
                self.client,
                message,
                embed = embed
            )
    
    async def pigeon(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._pigeon.getMinParameters():
            result = getErrorMessage(self._pigeon, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._pigeon.getMaxParameters():
            result = getErrorMessage(self._pigeon, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                pigeon.generateImage,
                parameters[0],
                parameters[1],
                parameters[2]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def playstation(self, message, parameters):
        """Generates and sends the brain size meme.
        """

        # Check if author voted on discordbots.org
        if await didAuthorVote(message.author):

            # Check for not enough parameters
            if len(parameters) < self._playstation.getMinParameters():
                result = getErrorMessage(self._playstation, Meme.NOT_ENOUGH_PARAMETERS)
            
            # Check for too many parameters
            elif len(parameters) > self._playstation.getMaxParameters():
                result = getErrorMessage(self._playstation, Meme.TOO_MANY_PARAMETERS)
            
            # There were the proper amount of parameters
            else:

                triangleText = ""
                squareText = ""

                # There were 2 parameters
                if len(parameters) == 2:
                    xText, circleText = parameters
                
                # There were 3 parameters
                elif len(parameters) == 3:
                    squareText, xText, circleText = parameters
                
                # There were 4 parameters
                else:
                    triangleText, squareText, xText, circleText = parameters

                result = await loop.run_in_executor(None,
                    playstation.generateImage,
                    triangleText,
                    squareText,
                    xText,
                    circleText
                )
            
            # Check if an error was made
            if type(result) == discord.Embed:
                await sendMessage(
                    self.client,
                    message,
                    embed = result
                )
            
            # No error was made, send image
            else:

                # Send message then remove image
                await sendMessage(
                    self.client,
                    message,
                    filename = result
                )

                os.remove(result)
        
        # Author did not vote
        else:
            embed = discord.Embed(
                title = "Vote!",
                description = "To run this command, you must [vote](https://discordbots.org/bot/503804826187071501/vote) for Omega Psi.",
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )

            await sendMessage(
                self.client,
                message,
                embed = embed
            )
    
    async def puppetMeme(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._puppetMeme.getMinParameters():
            result = getErrorMessage(self._puppetMeme, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._puppetMeme.getMaxParameters():
            result = getErrorMessage(self._puppetMeme, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                puppetMeme.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
        
    async def rewindTime(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._rewindTime.getMinParameters():
            result = getErrorMessage(self._rewindTime, Meme.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                rewindTime.generateImage,
                " ".join(parameters)
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def runAway(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._runAway.getMinParameters():
            result = getErrorMessage(self._runAway, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._runAway.getMaxParameters():
            result = getErrorMessage(self._runAway, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None, 
                runAway.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def saveOne(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._saveOne.getMinParameters():
            result = getErrorMessage(self._saveOne, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._saveOne.getMaxParameters():
            result = getErrorMessage(self._saveOne, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                saveOne.generateImage,
                parameters[0],
                parameters[1],
                parameters[2]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def sayItAgain(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._sayItAgain.getMinParameters():
            result = getErrorMessage(self._sayItAgain, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._sayItAgain.getMaxParameters():
            result = getErrorMessage(self._sayItAgain, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                sayItAgain.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
        
    async def soccerTongue(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._soccerTongue.getMinParameters():
            result = getErrorMessage(self._soccerTongue, Meme.NOT_ENOUGH_PARAMETERS)

        # Check for too many parameters
        elif len(parameters) > self._soccerTongue.getMaxParameters():
            result = getErrorMessage(self._soccerTongue, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                soccerTongue.generateImage,
                parameters[0],
                parameters[1]
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def spontaneousAnger(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._spontaneousAnger.getMinParameters():
            result = getErrorMessage(self._spontaneousAnger, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._spontaneousAnger.getMaxParameters():
            result = getErrorMessage(self._spontaneousAnger, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(
                spontaneousAnger.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def startLearning(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._startLearning.getMinParameters():
            result = getErrorMessage(self._startLearning, Meme.NOT_ENOUGH_PARAMETERS)

        # Check for too many parameters
        elif len(parameters) > self._startLearning.getMaxParameters():
            result = getErrorMessage(self._startLearning, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Check for an even amount of parameters (invalid amount)
            if len(parameters) % 2 == 0:
                result = getErrorMessage(self._startLearning, Meme.MISSING_PARAMETER)

            # There were an odd amount of parameters (valid)
            else:
                result = await loop.run_in_executor(None,
                    startLearning.generateImage,
                    parameters[0],
                    parameters[1],
                    parameters[2],
                    "" if len(parameters) < 5 else parameters[3],
                    "" if len(parameters) < 5 else parameters[4],
                    "" if len(parameters) < 7 else parameters[5],
                    "" if len(parameters) < 7 else parameters[6],
                    "" if len(parameters) < 9 else parameters[7],
                    "" if len(parameters) < 9 else parameters[8],
                    "" if len(parameters) < 11 else parameters[9],
                    "" if len(parameters) < 11 else parameters[10],
                    "" if len(parameters) < 13 else parameters[11],
                    "" if len(parameters) < 13 else parameters[12]       
                )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def surprisedDwight(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._surprisedDwight.getMinParameters():
            result = getErrorMessage(self._surprisedDwight, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._surprisedDwight.getMaxParameters():
            result = getErrorMessage(self._surprisedDwight, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
           result = await loop.run_in_executor(None, 
                surprisedDwight.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def surprisedPikachu(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._surprisedPikachu.getMinParameters():
            result = getErrorMessage(self._surprisedPikachu, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._surprisedPikachu.getMaxParameters():
            result = getErrorMessage(self._surprisedPikachu, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                surprisedPikachu.generateImage,
                parameters
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def thanosStone(self, message, parameters):
        """Generates and sends the Thanos Stone meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._thanosStone.getMinParameters():
            result = getErrorMessage(self._thanosStone, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._thanosStone.getMaxParameters():
            result = getErrorMessage(self._thanosStone, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                thanosStone.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def threeDoors(self, message, parameters):
        """Generates and sends the Brain Of meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._threeDoors.getMinParameters():
            result = getErrorMessage(self._threeDoors, Meme.NOT_ENOUGH_PARAMETERS)

        # Check for too many parameters
        elif len(parameters) > self._threeDoors.getMaxParameters():
            result = getErrorMessage(self._threeDoors, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                threeDoors.generateImage,
                parameters[0],
                parameters[1],
                parameters[2],
                "" if len(parameters) < 4 else parameters[3]
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def trojanHorse(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._trojanHorse.getMinParameters():
            result = getErrorMessage(self._trojanHorse, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._trojanHorse.getMaxParameters():
            result = getErrorMessage(self._trojanHorse, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None, 
                trojanHorse.generateImage,
                parameters[0],
                parameters[1],
                parameters[2],
                parameters[3]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def trump(self, message, parameters):
        """
        """

        # Check for not enough parameters
        if len(parameters) < self._trump.getMinParameters():
            result = getErrorMessage(self._trump, Meme.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                trump.generateImage,
                " ".join(parameters)
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def whoKilledHannibal(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._whoKilledHannibal.getMinParameters():
            result = getErrorMessage(self._whoKilledHannibal, Meme.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._whoKilledHannibal.getMaxParameters():
            result = getErrorMessage(self._whoKilledHannibal, Meme.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                whoKilledHannibal.generateImage,
                parameters[0],
                parameters[1],
                parameters[2],
                parameters[3]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def on_message(self, message):
        """Parses a message and runs a Meme Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if await Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(await Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Iterate through commands
            for cmd in self.getCommands():
                if command in cmd.getAlternatives():
                    async with message.channel.typing():

                        # Run the command but don't try running others
                        await self.run(message, cmd, cmd.getCommand(), message, parameters)
                    break

def setup(client):
    client.add_cog(Meme(client))