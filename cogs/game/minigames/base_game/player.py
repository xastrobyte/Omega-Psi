from abc import abstractmethod
from discord import Member

class Player:
    """A Player object that holds the important information for other possible game instances
    used in Omega Psi. When given a `str`, the player is set as an AI player.

    Keyword Parameters
    ------------------
    :param member: The Discord User defining this Player object or a string
        clarifying this Player object as an AI Player
    
    :param is_smart: Whether or not this Player is playing cleverly or randomly
        Note: This only applies to AI players
    """

    QUIT = "QUIT"

    # # # # # # # # # # # # # # # # # # # #

    def __init__(self, *, member = None, is_smart = None):
        self.member = member if isinstance(member, Member) else "AI {}".format(member)
        self.is_ai = not isinstance(member, Member) # Check if the player is an AI
        self.is_smart = is_smart if not isinstance(member, Member) else None
        self.id = member.id if isinstance(member, Member) else member

    # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # #

    @property
    def member(self):
        return self.__member

    @property
    def is_ai(self):
        return self.__is_ai

    @property
    def is_smart(self):
        return self.__is_smart
    
    @property
    def id(self):
        return self.__id

    # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # #

    @member.setter
    def member(self, member):
        self.__member = member

    @is_ai.setter
    def is_ai(self, is_ai):
        self.__is_ai = is_ai
    
    @is_smart.setter
    def is_smart(self, is_smart):
        self.__is_smart = is_smart
    
    @id.setter
    def id(self, id):
        self.__id = id
    
    # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # #

    @abstractmethod
    async def process_turn(self, game):
        """Processes the current turn for this player by waiting until they
        react to make their move or, if this player is an AI, choosing the best place
        to go

        :param game: The game object this player is connected to
        """
        pass

    # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # #

    def get_name(self):
        """Retrieves the name of this Player for simpler formatting.

        :rtype: str
        """

        # If the player is an AI, only the name is returned
        # If the player is a Discord Member, their name and discriminator is returned
        return str(self.member)
