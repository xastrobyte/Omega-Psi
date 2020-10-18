class CareerCard:
    """A Career Card contains information pertaining to the name of a career, the salary
    of a career, and the bonus number of a career

    :param name: The name of the career
    :param salary: The amount of money given to the player each payday
    :param bouns: The number that needs to be rolled for the player to receive bonus money
    :param json: A json object that holds the same values as the parameters specified above
    """

    def __init__(self, name = None, salary = None, bonus = None, *, json = None):
        
        # Check if the data for this career card is given through the JSON object
        if json:
            name = json["name"]
            salary = json["salary"]
            bonus = json["bonus"]
        
        # If not, verify that all the values are given
        #   if even one of them is missing, raise an error
        if not name or not salary or not bonus:
            raise TypeError("You must include the name, the salary, and the bonus number of the career card.")
        
        self.name = name
        self.salary = salary
        self.bonus = bonus
    
    def __str__(self):
        return "```md\n{}\n{}\n{}\n```".format(
            "[Job Title][{}]".format(self.name),
            "  <Salary ${:0,}>".format(self.salary),
            "  <Bonus {}>".format(self.bonus)
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def name(self):
        return self.__name
    
    @property
    def salary(self):
        return self.__salary
    
    @property
    def bonus(self):
        return self.__bonus

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @name.setter
    def name(self, name):
        self.__name = name
    
    @salary.setter
    def salary(self, salary):
        self.__salary = salary
    
    @bonus.setter
    def bonus(self, bonus):
        self.__bonus = bonus

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
class HouseCard:
    """A House Card contains information pertaining to the name of the house, the purchase price
    the spin red selling price and the spin black selling price

    :param name: The name of the house
    :param purchase: The price of the house
    :param spin_red: The amount of money given to the player if they spin red when selling the house
    :param spin_black: The amount of money given to the player if they spin black when selling the house
    :param json: A json object that holds the same values as the parameters specified above
    """

    def __init__(self, name = None, purchase = None, spin_red = None, spin_black = None, *, json = None):

        # Check if the data for this house card is given through the JSON object
        if json:
            name = json["name"]
            purchase = json["purchase"]
            spin_red = json["spin_red"]
            spin_black = json["spin_black"]
        
        # If not, verify that all the values are given
        #   if even one of them is missing, raise an error
        if not name or not purchase or not spin_red or not spin_black:
            raise TypeError("You must include the name, the purchase price, and the spin red/black values for this house card.")
        
        self.name = name
        self.purchase = purchase
        self.spin_red = spin_red
        self.spin_black = spin_black
    
    def __str__(self):
        return "```md\n{}\n{}\n{}\n{}\n{}\n```".format(
            "[House][{}]".format(self.name),
            "  <Cost ${:0,}>".format(self.purchase),
            "# When selling the house",
            "  <Red ${:0,}>".format(self.spin_red),
            "  <Black ${:0,}>".format(self.spin_black)
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def name(self):
        return self.__name
    
    @property
    def purchase(self):
        return self.__purchase
    
    @property
    def spin_red(self):
        return self.__spin_red

    @property
    def spin_black(self):
        return self.__spin_black

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @name.setter
    def name(self, name):
        self.__name = name
    
    @purchase.setter
    def purchase(self, purchase):
        self.__purchase = purchase
    
    @spin_red.setter
    def spin_red(self, spin_red):
        self.__spin_red = spin_red

    @spin_black.setter
    def spin_black(self, spin_black):
        self.__spin_black = spin_black

class PetCard:
    """A Pet Card contains information pertaining to the name of the card, the description
    the type of action, the amount of the card, whether or not the card adds a pet,
    and whether or not the money in the amount comes from/is paid to the bank.

    :param name: The name of the house
    :param action_text: The description of the pet card
    :param add: Whether or not the card adds pets to the player's car
    :param action: The type of action of the card
    :param amount: The amount of money paid or received
    :param bank: Whether or not the money comes from/is paid to the bank
    :param json: A json object that holds the same values as the parameters specified above
    """

    def __init__(self, name = None, action_text = None, add = None, action = None, amount = None, bank = None, *, json = None):

        # Check if the data for this house card is given through the JSON object
        if json:
            name = json["name"]
            action_text = json["action_text"]
            add = json["add"]
            action = json["action"]
            amount = json["amount"]
            bank = json["bank"]
        
        # If not, verify that all the values are given
        #   if even one of them is missing, raise an error
        if not name or not action_text or add == None or not action or not amount or bank == None:
            raise TypeError("You must include the name, the action text, the action, the amount, the add parameter, and the bank parameter for this PetCard.")
        
        self.name = name
        self.action_text = action_text
        self.add = add
        self.action = action
        self.amount = amount
        self.bank = bank

    def __str__(self):
        return "```md\n{}\n{}\n<\n{}\n>\n```".format(
            self.name,
            "=" * len(self.name),
            self.action_text
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def name(self):
        return self.__name
    
    @property
    def action_text(self):
        return self.__action_text
    
    @property
    def add(self):
        return self.__add

    @property
    def action(self):
        return self.__action

    @property
    def amount(self):
        return self.__amount
    
    @property
    def bank(self):
        return self.__bank

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @name.setter
    def name(self, name):
        self.__name = name
    
    @action_text.setter
    def action_text(self, action_text):
        self.__action_text = action_text

    @add.setter
    def add(self, add):
        self.__add = add
    
    @action.setter
    def action(self, action):
        self.__action = action
    
    @amount.setter
    def amount(self, amount):
        self.__amount = amount
    
    @bank.setter
    def bank(self, bank):
        self.__bank = bank

class ActionCard:
    """An Action Card contains information pertaining to the name of the card, the type of action
    any spin values (low, medium, high), the amounts of money received from those spaces,
    and whether or not the money comes from/is paid to the bank.

    :param name: The name of the card
    :param action: The specific action attributes of this card
    :param spin: The specific spin attributes of this card
    :param json: A json object that holds the same values as the parameters specified above
    """

    def __init__(self, name = None, action = None, spin = None, *, json = None):

        # Check if the data for this house card is given through the JSON object
        if json:
            name = json["name"]
            action = self.Action(json = json["action"])
            spin = self.Spin(json = json["spin"])
        
        # If not, verify that all the values are given
        #   if even one of them is missing, raise an error
        if not name or not action or not spin:
            raise TypeError("You must include the name, the action, and the spin value for this ActionCard.")
        
        self.name = name
        self.action = action
        self.spin = spin
    
    def __str__(self):

        # Check if the action card is where a player is fired from their
        #   current career
        if self.action.type == "fired":
            return "```md\n{}\n{}\n<\n{}>\n```".format(
                self.name, "=" * len(self.name),
                "{}{}{}{}".format(
                    "{}\n".format(self.action.text) if self.action.text != None else "",
                    "{}\n".format(self.spin.low),
                    "{}\n".format(self.spin.medium),
                    "{}\n".format(self.spin.high)
                )
            )
        
        # The action card is a normal card
        else:
            return "```md\n{}\n{}\n<\n{}>\n```".format(
                self.name,
                "=" * len(self.name),
                "{}{}{}{}".format(
                    "{}\n".format(self.action.text) if self.action.text != None else "",
                    "{}\n".format(self.spin.low.text) if self.spin.low != None else "",
                    "{}\n".format(self.spin.medium.text) if self.spin.medium != None else "",
                    "{}\n".format(self.spin.high.text) if self.spin.high != None else ""
                )
            )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def name(self):
        return self.__name
    
    @property
    def action(self):
        return self.__action
    
    @property
    def spin(self):
        return self.__spin

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @name.setter
    def name(self, name):
        self.__name = name
    
    @action.setter
    def action(self, action):
        self.__action = action
    
    @spin.setter
    def spin(self, spin):
        self.__spin = spin
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Nested Classes
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    class Action:
        """An Action object is used to hold specific information about the text and
        type of action card it belongs to

        :param text: Any specific action text that acts as a description of this ActionCard
        :param type: The type of action card this is
        :param target: The target player(s) of this action card
        :param special: Any special type of card this action card may be
        :param bank: Whether or not the money spun or received/paid comes from the bank
        :param json: A json object that holds the same values as the parameters specified above
        """

        def __init__(self, text = None, type = None, target = None, special = None, bank = None, *, json = None):

            # Check if the data for this house card is given through the JSON object
            if json:
                text = None if "text" not in json else json["text"]
                type = json["type"]
                target = None if "target" not in json else json["target"]
                special = None if "special" not in json else json["special"]
                bank = json["bank"]
            
            # If not, verify that all the values are given
            #   if even one of them is missing, raise an error
            if not type or bank == None:
                raise TypeError("You must include the type, the target, and the bank parameter for this Action.")
            
            self.text = text
            self.type = type
            self.target = target
            self.special = special
            self.bank = bank
        
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Getter
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        @property
        def text(self):
            return self.__text
        
        @property
        def type(self):
            return self.__type
        
        @property
        def target(self):
            return self.__target
        
        @property
        def special(self):
            return self.__special
        
        @property
        def bank(self):
            return self.__bank

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Setter
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        @text.setter
        def text(self, text):
            self.__text = text
        
        @type.setter
        def type(self, type):
            self.__type = type
        
        @target.setter
        def target(self, target):
            self.__target = target
        
        @special.setter
        def special(self, special):
            self.__special = special
        
        @bank.setter
        def bank(self, bank):
            self.__bank = bank
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    class Spin:
        """A Spin object is used to hold information about any spin action
        that is linked to this action card.
            For example, if a player has to spin 1-5 to collect 50k from the bank
                      or if a player has to spin 6-10 to collect 100k from the bank
        
        :param type: A type of "number" or "color" that describes if the player has to spin
            a number or a color to collect their reward/pay money
        :param low: A SpinType object that describes the low spinning value
        :param medium: A SpinType object that describes the medium spinning value
            Note that this is not required by every card
        :param high: A SpinType object that describes the high spinning value
        :param json: A json object that holds the same values as the parameters specified above
        """

        def __init__(self, type = None, low = None, high = None, medium = None, *, json = None):

            # Check if the data for this house card is given through the JSON object
            if json:

                # Check if the type of card is a FIRED card
                #   load the low, medium, and high spin types differently
                type = json["type"]
                if type == "fired":
                    low, medium, high = json["low"], json["medium"], json["high"]
                else:
                    low = None if json["low"] == None else self.SpinType(json = json["low"], type = type)
                    medium = None if json["medium"] == None else self.SpinType(json = json["medium"], type = type)
                    high = None if json["high"] == None else self.SpinType(json = json["high"], type = type)
                amount = json["amount"]
            
            # If not, verify that all the values are given
            #   if even one of them is missing, raise an error
            if not(amount or low and high):
                raise TypeError("You must include either the amount or the low spin value and the high spin value for this Spin.")
            
            self.type = type
            self.low = low
            self.medium = medium
            self.high = high
            self.amount = amount
        
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Getter
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        @property
        def type(self):
            return self.__type
        
        @property
        def low(self):
            return self.__low
        
        @property
        def medium(self):
            return self.__medium
        
        @property
        def high(self):
            return self.__high
        
        @property
        def amount(self):
            return self.__amount

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Setter
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        @type.setter
        def type(self, type):
            self.__type = type
        
        @low.setter
        def low(self, low):
            self.__low = low
        
        @medium.setter
        def medium(self, medium):
            self.__medium = medium
        
        @high.setter
        def high(self, high):
            self.__high = high
        
        @amount.setter
        def amount(self, amount):
            self.__amount = amount
        
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Nested Classes
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        class SpinType:
            """A SpinType contains information about the attributes of a low, high, or medium
            spinning action.

            :param text: The text that describes this specific spin value
            :param color: The name of the color that describes this SpinType
                Note that this parameter can only be None if
                the low and high parameters are specified
            :param low: The low value that this SpinType object holds
                Note that this parameter can only be None if
                the color parameter is specified
            :param high: The high value that this SpinType object holds
                Note that this parameter can only be None if
                the color parameter is specified
            :param amount: The amount that is received/paid by the target player of this card
            :param json: A json object that holds the same values as the parameters specified above
            :param type: A string determining if the SpinType is of type color
                if so, the low and high values are brought in from red and black colors
            """

            def __init__(self, text = None, color = None, low = None, high = None, amount = None, *, json = None, type = None):

                # Check if the data for this house card is given through the JSON object
                if json:

                    # Check if the type is color
                    text = json["text"]
                    if type == "color":
                        color = json["color"]
                    else:
                        low, high = json["low"], json["high"]
                    amount = json["amount"]
                
                # If not, verify that all the values are given
                #   if even one of them is missing, raise an error
                if not text or not amount or not(color or low and high):
                    raise TypeError("You must include the text, the low value, the high value, and the amount for this SpinType.")
                
                self.text = text
                self.color = color
                self.low = low
                self.high = high
                self.amount = amount
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # Getter
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            @property
            def text(self):
                return self.__text
            
            @property
            def low(self):
                return self.__low
            
            @property
            def high(self):
                return self.__high
            
            @property
            def amount(self):
                return self.__amount

            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # Setter
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            @text.setter
            def text(self, text):
                self.__text = text
            
            @low.setter
            def low(self, low):
                self.__low = low
            
            @high.setter
            def high(self, high):
                self.__high = high
            
            @amount.setter
            def amount(self, amount):
                self.__amount = amount

class BoardSpace:
    """A Board Space contains information about the next space in the board,
    the type of space, whether or not the space is a STOP sign space,
    or, if there are two paths to a space, which space comes next depending on the player's choice

    :param space: The identifying value of the current space
    :param type: The type of space
    :param path: The identifying path of the space
    :param stop: Whether or not this space is a stop space
    :param next: The space that follows this current space
        Note that this parameter can only be None if 
        the next_true and next_false parameters are specified
    :param next_true: The space that follows this current space when the player decides
        to go to a specific path
        Note that this parameter can only be None if
        the next parameter is specified
    :param next_space: The space that follows this current space when the player decides
        to stay on their current path
        Note that this parameter can only be None if
        the next parameter is specified
    :param json: A json object that holds the same values as the parameters specified above
    """

    def __init__(self, space = None, type = None, path = None, stop = None, next = None, next_true = None, next_false = None, spin = None, amount = None, *, json = None):

        # Check if the data for this house card is given through the JSON object
        if json:
            type = json["type"]
            path = json["path"]
            stop = json["stop"]

            # Check if the type of this space is the retirement space
            #   we don't need to worry about the next, next_true, or next_false values
            #   because there is nowhere else to go
            next = None if ("next_true" in json and "next_false" in json or type == "retirement") else json["next"]
            next_true = None if ("next" in json or type == "retirement") else json["next_true"]
            next_false = None if ("next" in json or type == "retirement") else json["next_false"]
            
            # Check if the type of this space is a spin_for_babies space
            #   get the spin values
            spin = None if type != "spin_for_babies" else json["spin"]
        
            # Check if the type of this space is a pay_money or get_money space
            #   get the amount
            amount = None if type not in ["pay_money", "get_money"] else json["amount"]
        
        # If not, verify that all the values are given
        #   if even one of them is missing, raise an error unless
        #   the current space is the retirement space
        if not path or stop == None or (not(next or next_true and next_false) and type != "retirement"):
            raise TypeError("You must include the type, the path, the stop parameter, and either the next value or the next_true and next_false value for this BoardSpace.")
        
        self.space = space
        self.type = type
        self.path = path
        self.stop = stop
        self.next = next
        self.next_true = next_true
        self.next_false = next_false
        self.spin = spin
        self.amount = amount
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def space(self):
        return self.__space

    @property
    def type(self):
        return self.__type
    
    @property
    def path(self):
        return self.__path
    
    @property
    def stop(self):
        return self.__stop
    
    @property
    def next(self):
        return self.__next
    
    @property
    def next_true(self):
        return self.__next_true
    
    @property
    def next_false(self):
        return self.__next_false
    
    @property
    def spin(self):
        return self.__spin
    
    @property
    def amount(self):
        return self.__amount

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @space.setter
    def space(self, space):
        self.__space = space

    @type.setter
    def type(self, type):
        self.__type = type
    
    @path.setter
    def path(self, path):
        self.__path = path
    
    @stop.setter
    def stop(self, stop):
        self.__stop = stop
    
    @next.setter
    def next(self, next):
        self.__next = next
    
    @next_true.setter
    def next_true(self, next_true):
        self.__next_true = next_true
    
    @next_false.setter
    def next_false(self, next_false):
        self.__next_false = next_false
    
    @spin.setter
    def spin(self, spin):
        self.__spin = spin
    
    @amount.setter
    def amount(self, amount):
        self.__amount = amount