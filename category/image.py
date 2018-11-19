from util.file.server import Server
from util.file.omegaPsi import OmegaPsi

from util.image import burnLetter
from util.image import butILikeThis
from util.image import carSkidding
from util.image import cardSlam
from util.image import classroomStares
from util.image import icarlyStopSign
from util.image import mastersBlessing
from util.image import nArmHandshake
from util.image import puppetMeme
from util.image import runAway
from util.image import saveOne
from util.image import sayItAgain
from util.image import spontaneousAnger
from util.image import surprisedDwight
from util.image import surprisedPikachu
from util.image import trojanHorse
from util.image import whoKilledHannibal

from util.utils import sendMessage, getErrorMessage, run

from random import choice as choose
from supercog import Category, Command
import discord, json, os, urllib.request, requests

class Image(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    EMBED_COLOR = 0x800080

    MEME_SUBREDDITS = [
        "meme",
        "memes",
        "dankmeme",
        "dank_meme"
    ]
    MEME_RANDOM = "https://www.reddit.com/r/{}/.json?sort=top&limit=500"

    REDDIT_BASE = "https://www.reddit.com"

    NASA_RANDOM = "https://images-api.nasa.gov/search?media_type=image&year_start=1960"
    NASA_SEARCH = "https://images-api.nasa.gov/search?q={}&media_type=image"
    DESCRIPTION_THRESHOLD = 2000

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    NO_GIFS_FOUND = "NO_GIFS_FOUND"
    NO_IMAGE = "NO_IMAGE"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Image",
            description = "Anything having to do with images is here.",
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._gif = Command(commandDict = {
            "alternatives": ["gif", "giphy", "g"],
            "info": "Sends a random gif from Giphy.",
            "parameters": {
                "keywords": {
                    "optional": True,
                    "info": "The keywords to search for in Giphy."
                }
            },
            "errors": {
                Image.NO_GIFS_FOUND: {
                    "messages": [
                        "Hmmm. No gifs were found with those keywords. Perhaps broaden your search?"
                    ]
                }
            }
        })

        self._theOffice = Command(commandDict = {
            "alternatives": ["theOffice", "office", "o"],
            "info": "Sends a random gif related to The Office.",
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "*Why are you the way that you are?* You don't need any parameters."
                    ]
                }
            }
        })

        self._parksAndRec = Command(commandDict = {
            "alternatives": ["parksAndRec", "parks", "pnr"],
            "info": "Sends a random gif related to Parks and Rec.",
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "No no no. You don't need any parameters to get a gif from Parks and Rec."
                    ]
                }
            }
        })

        self._brooklyn99 = Command(commandDict = {
            "alternatives": ["brooklyn99", "b99", "99"],
            "info": "Sends a random gif related to Brooklyn Nine-Nine.",
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "No doubt no doubt no doubt you need no parameters for this command."
                    ]
                }
            }
        })

        self._meme = Command(commandDict = {
            "alternatives": ["meme"],
            "info": "Sends a random meme from Reddit.",
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a meme, you don't need any parameters."
                    ]
                },
                Image.NO_IMAGE: {
                    "messages": [
                        "Somehow there were no memes found??? Idk try again."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To generate this meme, you need to give at least 3 sets of text wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters for this. You only need 3 sets of text wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 3 sets of text each wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text each wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need the bubble text to generate this meme."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need the bubble text to generate this meme."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need 3 parameters to generate this meme."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need 3 different texts to put on the meme."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 3 sets of text each wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text each wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 3 sets of text wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you can have up to 5 sets of text wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 3 sets of text each wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text each wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 2 sets of text each wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text each wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 2 sets of text each wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text each wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 2 sets of text each wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text each wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 3 lines to add."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "There is a maximum of 5 lines you can put on this meme."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 4 sets of text wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 4 sets of text wrapped in quotes (\")."
                    ]
                }
            }
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 4 sets of text wrapped in quotes (\")."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 4 sets of text wrapped in quotes (\")."
                    ]
                }
            }
        })

        self._nasaImage = Command(commandDict = {
            "alternatives": ["nasa", "NASA", "nasaImage", "NASAImage", "nasaImg", "NASAImg"],
            "info": "Gives you a random NASA image given a search term or no search term.",
            "parameters": {
                "term": {
                    "info": "The term to search for a NASA image.",
                    "optional": True
                }
            },
            "errors": {
                Image.NO_IMAGE: {
                    "messages": [
                        "There were no images matching that search. Try again or broaden your search term."
                    ]
                }
            }
        })

        self.setCommands([
            self._gif,
            self._theOffice,
            self._parksAndRec,
            self._brooklyn99,

            self._meme,
            self._burnLetter,
            self._butILikeThis,
            self._carSkidding,
            self._cardSlam,
            self._classroomStares,
            self._icarlyStopSign,
            self._mastersBlessing,
            self._nArmHandshake,
            self._puppetMeme,
            self._runAway,
            self._saveOne,
            self._sayItAgain,
            self._spontaneousAnger,
            self._surprisedDwight,
            self._surprisedPikachu,
            self._trojanHorse,
            self._whoKilledHannibal,

            self._nasaImage
        ])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def gif(self, keywords):
        """Returns a gif from giphy.\n

         - keywords - The keywords to search by.\n
        """

        # Get data involving gifs from Giphy
        if keywords == "random":
            with urllib.request.urlopen(os.environ["GIPHY_RANDOM_API_URL"]) as url:
                gifData = url.read()
            gifData = json.loads(gifData)
        
        else:
            with urllib.request.urlopen(
                os.environ["GIPHY_SEARCH_API_URL"].format(
                    keywords.replace(" ", "+")
                )
            ) as url:
                gifsData = url.read()
            gifsData = json.loads(gifsData)

            # Return random embed url
            if len(gifsData) > 0:
                gifData = choose(gifsData["data"])
            else:
                return getErrorMessage(self._gif, Image.NO_GIFS_FOUND)
        
        return gifData["embed_url"]
    
    def meme(self, channel):
        """Returns a random meme from Reddit.\n

        Parameters:
            channel (discord.Channel): The channel to send to. Helps to determine NSFW memes
        """

        # See if channel has is_nsfw
        try:
            isNSFW = channel.is_nsfw()
        
        # Channel is private, allow NSFW
        except:
            isNSFW = True

        # Get data involving Reddit memes
        # Choose random subreddit between meme subreddits (meme, memes, dankmemes, dank_meme)
        subreddit = choose(Image.MEME_SUBREDDITS)

        redditData = requests.get(
            Image.MEME_RANDOM.format(subreddit),
            headers = {
                "User-agent": "Omega Psi"
            }
        ).json()

        # Make sure there are reddit posts
        if len(redditData["data"]["children"]) == 0:
            return getErrorMessage(self._meme, Image.NO_IMAGE)
        
        # Choose random reddit post
        redditPost = choose(redditData["data"]["children"])["data"]
        while redditPost["is_video"] or (redditPost["over_18"] and not isNSFW):
            redditPost = choose(redditData["data"]["children"])["data"]

        # Return an embed for the reddit post
        return discord.Embed(
            name = "Meme Result",
            description = "[{}]({})".format(
                redditPost["title"],
                Image.REDDIT_BASE + redditPost["permalink"]
            ),
            colour = Image.EMBED_COLOR
        ).set_image(
            url = redditPost["url"]
        ).set_footer(
            text = "👍 {} 💬 {}".format(
                redditPost["score"],
                redditPost["num_comments"]
            )
        )
    
    def nasaImage(self, keywords):
        """Returns an image from NASA.\n

         - keywords - The keywords to search by.\n
        """

        # Get data involving NASA images
        if keywords == "random":
            with urllib.request.urlopen(Image.NASA_RANDOM) as url:
                imageData = url.read()
            imageData = json.loads(imageData)

        else:
            with urllib.request.urlopen(Image.NASA_SEARCH.format(
                keywords.replace(" ", "+")
            )) as url:
                imageData = url.read()
            imageData = json.loads(imageData)

        # Check if there are no images
        if len(imageData["collection"]["items"]) == 0:
            return getErrorMessage(self._nasaImage, Image.NO_IMAGE)
        
        # Choose random item from collection
        item = choose(imageData["collection"]["items"])

        # Get href from item
        imageLink = item["links"][0]["href"]

        # Make sure description is less than 2000 characters
        if len(item["data"][0]["description"]) < Image.DESCRIPTION_THRESHOLD:
            description = item["data"][0]["description"]
        else:
            description = item["data"][0]["description"][:Image.DESCRIPTION_THRESHOLD] + "[...]"

        return discord.Embed(
            title = item["data"][0]["title"],
            description = description,
            colour = Image.EMBED_COLOR
        ).set_image(
            url = imageLink
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs an Image Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Gif Command
            if command in self._gif.getAlternatives():
                result = await run(message, self._gif, self.gif, " ".join(parameters) if len(parameters) > 0 else "random")

                if type(result) == discord.Embed:
                    await sendMessage(
                        self.client,
                        message,
                        embed = result
                    )
                
                else:
                    await sendMessage(
                        self.client,
                        message,
                        message = result
                    )
            
            # The Office Command
            elif command in self._theOffice.getAlternatives():
                
                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        message = await run(message, self._theOffice, self.gif, "the office")
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._theOffice, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Parks and Rec Command
            elif command in self._parksAndRec.getAlternatives():
                
                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        message = await run(message, self._parksAndRec, self.gif, "parks and rec")
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._parksAndRec, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Brooklyn 99 Command
            elif command in self._brooklyn99.getAlternatives():
                
                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        message = await run(message, self._brooklyn99, self.gif, "brooklyn 99")
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._brooklyn99, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Meme Command
            elif command in self._meme.getAlternatives():
                result = await run(message, self._meme, self.meme, message.channel)

                if type(result) == discord.Embed:
                    await sendMessage(
                        self.client,
                        message,
                        embed = result
                    )
                
            # Burn Letter Command
            elif command in self._burnLetter.getAlternatives():

                # Less than 2 Parameters Exist
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._burnLetter, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 2 Parameters Exist
                elif len(parameters) == 2:
                    result = await run(message, self._burnLetter, burnLetter.generateImage, parameters[0], parameters[1])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 2 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._burnLetter, Category.TOO_MANY_PARAMETERS)
                    )
            
            # But I Like This Command
            elif command in self._butILikeThis.getAlternatives():

                # Less than 2 Parameters Exist
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._butILikeThis, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 2 Parameters Exist
                elif len(parameters) == 2:
                    result = await run(message, self._butILikeThis, butILikeThis.generateImage, parameters[0], parameters[1])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 2 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._butILikeThis, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Car Skidding Command
            elif command in self._carSkidding.getAlternatives():

                # Less than 3 Parameters Exist
                if len(parameters) < 3:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._carSkidding, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 3 Parameters Exist
                elif len(parameters) == 3:
                    result = await run(message, self._carSkidding, carSkidding.generateImage, parameters[0], parameters[1], parameters[2])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 3 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._carSkidding, Category.TOO_MANY_PARAMETERS)
                    )
                
            # Card Slam Command
            elif command in self._cardSlam.getAlternatives():
                
                # Less than 3 Parameters Exist
                if len(parameters) < 3:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._cardSlam, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 3 Parameters Exist
                elif len(parameters) == 3:
                    result = await run(message, self._cardSlam, cardSlam.generateImage, parameters[0], parameters[1], parameters[2])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )
                    
                    os.remove(result) # Remove temporary image
                
                # More than 3 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._cardSlam, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Classroom Stares Command
            elif command in self._classroomStares.getAlternatives():

                # Less than 1 Parameter Exist
                if len(parameters) < 1:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._classroomStares, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 3 Parameters Exist
                elif len(parameters) == 3:
                    result = await run(message, self._classroomStares, classroomStares.generateImage, parameters[0])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 1 Parameter Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._classroomStares, Category.TOO_MANY_PARAMETERS)
                    )
                
            # iCarly Stop Sign Command
            elif command in self._icarlyStopSign.getAlternatives():

                # Less than 2 Parameters exist
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._icarlyStopSign, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 3 Parameters Exist
                elif len(parameters) in [2, 3]:

                    if len(parameters) == 2:
                        spencerText = parameters[0]
                        stopText = ""
                        gibbyText = parameters[1]
                    else:
                        spencerText = parameters[0]
                        stopText = parameters[1]
                        gibbyText = parameters[2]

                    result = await run(message, self._icarlyStopSign, icarlyStopSign.generateImage, spencerText, stopText, gibbyText)

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )
                    
                    os.remove(result) # Remove temporary image
                
                # More than 3 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._icarlyStopSign, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Masters Blessing Command
            elif command in self._mastersBlessing.getAlternatives():
                
                # Less than 3 Parameters Exist
                if len(parameters) < 3:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._mastersBlessing, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 3 Parameters Exist
                elif len(parameters) == 3:
                    result = await run(message, self._mastersBlessing, mastersBlessing.generateImage, parameters[0], parameters[1], parameters[2])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )
                    
                    os.remove(result) # Remove temporary image
                
                # More than 3 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._mastersBlessing, Category.TOO_MANY_PARAMETERS)
                    )
                
            # N Arm Handshake Command
            elif command in self._nArmHandshake.getAlternatives():

                # Less than 3 Parameters Exist
                if len(parameters) < 3:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._nArmHandshake, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 3 to 5 Parameters Exist
                elif len(parameters) in [3, 4, 5]:
                    
                    if len(parameters) == 4:
                        thirdArm = parameters[3]
                        fourthArm = None
                    elif len(parameters) == 5:
                        thirdArm = parameters[3]
                        fourthArm = parameters[4]
                    else:
                        thirdArm = None
                        fourthArm = None

                    result = await run(message, self._nArmHandshake, nArmHandshake.generateImage, parameters[0], parameters[1], parameters[2], thirdArm, fourthArm)

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 5 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._nArmHandshake, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Puppet Meme Command
            elif command in self._puppetMeme.getAlternatives():

                # Less than 2 Parameters Exist
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._puppetMeme, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 2 Parameters Exist
                elif len(parameters) == 2:
                    result = await run(message, self._puppetMeme, puppetMeme.generateImage, parameters[0], parameters[1])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 2 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._puppetMeme, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Run Away Command
            elif command in self._runAway.getAlternatives():

                # Less than 2 Parameters Exist
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._runAway, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 2 Parameters Exist
                elif len(parameters) == 2:
                    result = await run(message, self._runAway, runAway.generateImage, parameters[0], parameters[1])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 2 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._runAway, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Save One Command
            elif command in self._saveOne.getAlternatives():

                # Less than 3 Parameters Exist
                if len(parameters) < 3:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._saveOne, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 3 Parameters Exist
                elif len(parameters) == 3:
                    result = await run(message, self._saveOne, saveOne.generateImage, parameters[0], parameters[1], parameters[2])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 3 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._saveOne, Category.TOO_MANY_PARAMETERS)
                    )
                
            # Say It Again Command
            elif command in self._sayItAgain.getAlternatives():

                # Less than 2 Parameters Exist
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._sayItAgain, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 2 Parameters Exist
                elif len(parameters) == 2:
                    result = await run(message, self._sayItAgain, sayItAgain.generateImage, parameters[0], parameters[1])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 2 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._sayItAgain, Category.TOO_MANY_PARAMETERS)
                    )

            # Spontaneous Anger Command
            elif command in self._spontaneousAnger.getAlternatives():

                # Less than 2 Parameters Exist
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._spontaneousAnger, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 2 Parameters Exist
                elif len(parameters) == 2:
                    result = await run(message, self._spontaneousAnger, spontaneousAnger.generateImage, parameters[0], parameters[1])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 2 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._spontaneousAnger, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Surprised Dwight Command
            elif command in self._surprisedDwight.getAlternatives():

                # Less than 2 Parameters Exist
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._carSkidding, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 2 Parameters Exist
                elif len(parameters) == 2:
                    result = await run(message, self._surprisedDwight, surprisedDwight.generateImage, parameters[0], parameters[1])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 3 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._surprisedDwight, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Surprised Pikachu Command
            elif command in self._surprisedPikachu.getAlternatives():

                # Less than 3 parameters exist
                if len(parameters) < 3:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._surprisedPikachu, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 3 to 5 parameters exist
                elif len(parameters) in [3, 4, 5]:
                    result = await run(message, self._surprisedPikachu, surprisedPikachu.generateImage, parameters)

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 5 parameters exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._surprisedPikachu, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Trojan Horse Command
            elif command in self._trojanHorse.getAlternatives():

                # Less than 4 Parameters Exist
                if len(parameters) < 4:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._trojanHorse, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 4 Parameters Exist
                elif len(parameters) == 4:
                    result = await run(message, self._trojanHorse, trojanHorse.generateImage, parameters[0], parameters[1], parameters[2], parameters[3])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 4 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._trojanHorse, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Who Killed Hannibal Command
            elif command in self._whoKilledHannibal.getAlternatives():

                # Less than 4 Parameters Exist
                if len(parameters) < 4:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._whoKilledHannibal, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 4 Parameters Exist
                elif len(parameters) == 4:
                    result = await run(message, self._whoKilledHannibal, whoKilledHannibal.generateImage, parameters[0], parameters[1], parameters[2], parameters[3])

                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
                
                # More than 4 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._whoKilledHannibal, Category.TOO_MANY_PARAMETERS)
                    )

            # NASA Image Command
            elif command in self._nasaImage.getAlternatives():
                result = await run(message, self._nasaImage, self.nasaImage, " ".join(parameters) if len(parameters) > 0 else "random")

                if type(result) == discord.Embed:
                    await sendMessage(
                        self.client,
                        message,
                        embed = result
                    )
                
                else:
                    await sendMessage(
                        self.client,
                        message,
                        message = result
                    )

def setup(client):
    client.add_cog(Image(client))
