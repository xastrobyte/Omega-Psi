from functools import partial
from random import choice

from category.globals import loop

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Data:
    def __init__(self, data):
        self._data = data
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_hangman_data_sync(self):
        
        # Get hangman data
        return self._data.find_one({"_id": "hangman"})
    
    def set_hangman_data_sync(self, hangman_data):
        
        # Set hangman data
        self._data.update_one(
            {"_id": "hangman"},
            {"$set": hangman_data},
            upsert = False
        )
    
    def add_pending_hangman_word_sync(self, phrase, author, email):
        
        # Get hangman data
        hangman_data = self.get_hangman_data_sync()

        # Add the phrase to the pending hangmans
        hangman_data["pending_hangman"].append({
            "phrase": phrase,
            "author": author,
            "email": email
        })

        # Set hangman data
        self.set_hangman_data_sync(hangman_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_scramble_data_sync(self):
        
        # Get scramble data
        return self._data.find_one({"_id": "scramble"})
    
    def set_scramble_data_sync(self, scramble_data):
        
        # Set scramble data
        self._data.update_one(
            {"_id": "scramble"},
            {"$set": scramble_data},
            upsert = False
        )
    
    def add_pending_scramble_word_sync(self, phrase, author, email):
        
        # Get scramble data
        scramble_data = self.get_scramble_data_sync()

        # Add the phrase to the pending scrambles
        scramble_data["pending_scramble"].append({
            "phrase": phrase,
            "author": author,
            "email": email,
            "hints": []
        })

        # Set scramble data
        self.set_scramble_data_sync(scramble_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_insult_data_sync(self):
        
        # Get insult data
        return self._data.find_one({"_id": "insults"})
    
    def set_insult_data_sync(self, insult_data):
        
        # Set insult data
        self._data.update_one(
            {"_id": "insults"},
            {"$set": insult_data},
            upsert = False
        )
    
    def add_pending_insult_sync(self, insult, author, email):
        
        # Get insult data
        insult_data = self.get_insult_data_sync()

        # Add insult to pending insult
        insult_data["pending_insults"].append({
            "insult": insult,
            "author": author,
            "email": email,
            "tags": []
        })
    
        # Set insult data
        self.set_insult_data_sync(insult_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_hangman_data(self):

        # Get hangman data
        hangman_data = await loop.run_in_executor(None,
            partial(
                self._data.find_one,
                {"_id": "hangman"}
            )
        )

        return hangman_data
    
    async def set_hangman_data(self, hangman_data):

        # Set hangman data
        await loop.run_in_executor(None,
            partial(
                self._data.update_one,
                {"_id": "hangman"},
                {"$set": hangman_data},
                upsert = False
            )
        )
    
    async def add_hangman_word(self, phrase):

        # Get hangman data
        hangman_data = await self.get_hangman_words()

        hangman_data["words"].append({
            "value": phrase,
            "level": "None"
        })

        # Set hangman data
        await self.set_hangman_words(hangman_data)
    
    async def get_hangman_words(self):
        return await self.get_hangman_data()
    
    async def set_hangman_words(self, hangman_words):
        await self.set_hangman_data(hangman_words)
    
    async def add_pending_hangman(self, phrase, author):
        
        # Get pending hangman data
        pending_hangman_data = await self.get_pending_hangman()

        # Add the phrase to the pending hangmans
        pending_hangman_data.append({
            "phrase": phrase,
            "author": author
        })

        # Set pending hangman data
        await self.set_pending_hangman(pending_hangman_data)
    
    async def get_pending_hangman(self):
        
        # Get hangman data
        hangman_data = await self.get_hangman_data()

        return hangman_data["pending_hangman"]
    
    async def set_pending_hangman(self, pending_hangman_data):
        
        # Get hangman data
        hangman_data = await self.get_hangman_data()

        hangman_data["pending_hangman"] = pending_hangman_data

        # Set hangman data
        await self.set_hangman_data(hangman_data)
    
    async def approve_pending_hangman(self, index):
        
        # Get pending hangman data
        pending_hangman_data = await self.get_pending_hangman()

        pending_hangman = pending_hangman_data.pop(index)

        # Set pending hangman data
        await self.set_pending_hangman(pending_hangman_data)

        # Add hangman phrase
        await self.add_hangman_word(pending_hangman["phrase"])
    
    async def deny_pending_hangman(self, index):
        
        # Get pending hangman data
        pending_hangman_data = await self.get_pending_hangman()

        pending_hangman_data.pop(index)

        # Set pending hangman data
        await self.set_pending_hangman(pending_hangman_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_scramble_data(self):

        # Get scramble data
        scramble_data = await loop.run_in_executor(None,
            partial(
                self._data.find_one,
                {"_id": "scramble"}
            )
        )

        return scramble_data
    
    async def set_scramble_data(self, scramble_data):

        # Set scramble data
        await loop.run_in_executor(None,
            partial(
                self._data.update_one,
                {"_id": "scramble"},
                {"$set": scramble_data},
                upsert = False
            )
        )
    
    async def add_scramble_word(self, phrase, hints):

        # Get scramble data
        scramble_data = await self.get_scramble_words()

        scramble_data["words"].append({
            "value": phrase,
            "hints": hints
        })

        # Set scramble data
        await self.set_scramble_words(scramble_data)
    
    async def get_scramble_words(self):
        return await self.get_scramble_data()
    
    async def set_scramble_words(self, scramble_words):
        await self.set_scramble_data(scramble_words)
    
    async def add_pending_scramble(self, phrase, author):
        
        # Get pending scramble data
        pending_scramble_data = await self.get_pending_scramble()

        # Add the phrase to the pending scrambles
        pending_scramble_data.append({
            "phrase": phrase,
            "author": author,
            "hints": []
        })

        # Set pending scramble data
        await self.set_pending_scramble(pending_scramble_data)
    
    async def add_pending_scramble_hints(self, index, hints = []):

        # Get pending scramble data
        pending_scramble_data = await self.get_pending_scramble()

        # Add the hints to the proper index
        pending_scramble_data[index]["hints"] += hints

        # Set pending scramble data
        await self.set_pending_scramble(pending_scramble_data)
    
    async def get_pending_scramble(self):
        
        # Get scramble data
        scramble_data = await self.get_scramble_data()

        return scramble_data["pending_scramble"]
    
    async def set_pending_scramble(self, pending_scramble_data):
        
        # Get scramble data
        scramble_data = await self.get_scramble_data()

        scramble_data["pending_scramble"] = pending_scramble_data

        # Set scramble data
        await self.set_scramble_data(scramble_data)
    
    async def approve_pending_scramble(self, index):
        
        # Get pending scramble data
        pending_scramble_data = await self.get_pending_scramble()

        pending_scramble = pending_scramble_data.pop(index)

        # Set pending scramble data
        await self.set_pending_scramble(pending_scramble_data)

        # Add scramble phrase
        await self.add_scramble_word(
            pending_scramble["phrase"],
            pending_scramble["hints"]
        )
    
    async def deny_pending_scramble(self, index):
        
        # Get pending scramble data
        pending_scramble_data = await self.get_pending_scramble()

        pending_scramble_data.pop(index)

        # Set pending scramble data
        await self.set_pending_scramble(pending_scramble_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_cards_against_humanity_cards(self):

        # Get cards against humanity data
        cah_data = await loop.run_in_executor(None,
            partial(
                self._data.find_one,
                {"_id": "cards_against_humanity"}
            )
        )

        return cah_data
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_insult_data(self):

        default = {
            "pending_insults": [],
            "insults": []
        }

        # Get insult data
        insult_data = await loop.run_in_executor(None,
            partial(
                self._data.find_one,
                {"_id": "insults"}
            )
        )

        if insult_data == None:
            await loop.run_in_executor(None,
                partial(
                    self._data.insert_one,
                    {"_id": "insults"}
                )
            )
            await self.set_insult_data(default)
            insult_data = default
        
        return insult_data
    
    async def set_insult_data(self, insult_data):

        # Set insult data
        await loop.run_in_executor(None,
            partial(
                self._data.update_one,
                {"_id": "insults"}, 
                {"$set": insult_data}, 
                upsert = False
            )
        )
    
    async def get_pending_insults(self):

        # Get insult data
        insult_data = await self.get_insult_data()

        return insult_data["pending_insults"]
    
    async def set_pending_insults(self, pending_insults):

        # Get insult data
        insult_data = await self.get_insult_data()

        insult_data["pending_insults"] = pending_insults

        # Set insult data
        await self.set_insult_data(insult_data)
    
    async def add_pending_insult(self, insult, author):

        # Get pending insults
        pending_insults = await self.get_pending_insults()

        pending_insults.append({
            "insult": insult,
            "author": author,
            "tags": []
        })

        # Set pending insults
        await self.set_pending_insults(pending_insults)
    
    async def add_pending_insult_tags(self, index, tags = []):

        # Get pending insults
        pending_insults = await self.get_pending_insults()

        for tag in tags:
            if tag.lower() not in pending_insults[index]["tags"]:
                pending_insults[index]["tags"].append(tag.lower())

        # Set pending insults
        await self.set_pending_insults(pending_insults)
    
    async def approve_pending_insult(self, index):

        # Get pending insults
        pending_insults = await self.get_pending_insults()

        # Remove insult
        insult = pending_insults.pop(index)

        # Set pending insults
        await self.set_pending_insults(pending_insults)

        # Get insults
        insults = await self.get_insults()

        # Add insult
        insults.append(insult)

        # Set insults
        await self.set_insults(insults)
    
    async def deny_pending_insult(self, index):

        # Get pending insults
        pending_insults = await self.get_pending_insults()

        # Remove insult
        pending_insults.pop(index)

        # Set pending insults
        await self.set_pending_insults(pending_insults)
    
    async def get_insults(self):

        # Get insult data
        insult_data = await self.get_insult_data()

        return insult_data["insults"]
    
    async def set_insults(self, insults):

        # Get insult data
        insult_data = await self.get_insult_data()

        insult_data["insults"] = insults

        # Set insult data
        await self.set_insult_data(insult_data)
    
    async def get_insult(self, nsfw = False):

        # Get insults
        insults = await self.get_insults()

        while True:
            insult = choice(insults)

            if nsfw or "nsfw" not in insult["tags"]:
                return insult
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_compliment_data(self):

        default = {
            "pending_compliments": [],
            "compliments": []
        }

        # Get compliment data
        compliment_data = await loop.run_in_executor(None,
            partial(
                self._data.find_one,
                {"_id": "compliments"}
            )
        )

        if compliment_data == None:
            await loop.run_in_executor(None,
                partial(
                    self._data.insert_one,
                    {"_id": "compliments"}
                )
            )
            await self.set_compliment_data(default)
            compliment_data = default
        
        return compliment_data
    
    async def set_compliment_data(self, compliment_data):

        # Set compliment data
        await loop.run_in_executor(None,
            partial(
                self._data.update_one,
                {"_id": "compliments"}, 
                {"$set": compliment_data}, 
                upsert = False
            )
        )
    
    async def get_pending_compliments(self):

        # Get compliment data
        compliment_data = await self.get_compliment_data()

        return compliment_data["pending_compliments"]
    
    async def set_pending_compliments(self, pending_compliments):

        # Get compliment data
        compliment_data = await self.get_compliment_data()

        compliment_data["pending_compliments"] = pending_compliments

        # Set compliment data
        await self.set_compliment_data(compliment_data)
    
    async def add_pending_compliment(self, compliment, author):

        # Get pending compliments
        pending_compliments = await self.get_pending_compliments()

        pending_compliments.append({
            "compliment": compliment,
            "author": author,
            "tags": []
        })

        # Set pending compliments
        await self.set_pending_compliments(pending_compliments)
    
    async def add_pending_compliment_tags(self, index, tags = []):

        # Get pending compliments
        pending_compliments = await self.get_pending_compliments()

        for tag in tags:
            if tag.lower() not in pending_compliments[index]["tags"]:
                pending_compliments[index]["tags"].append(tag.lower())

        # Set pending compliments
        await self.set_pending_compliments(pending_compliments)
    
    async def approve_pending_compliment(self, index):

        # Get pending compliments
        pending_compliments = await self.get_pending_compliments()

        # Remove compliment
        compliment = pending_compliments.pop(index)

        # Set pending compliments
        await self.set_pending_compliments(pending_compliments)

        # Get compliments
        compliments = await self.get_compliments()

        # Add compliment
        compliments.append(compliment)

        # Set compliments
        await self.set_compliments(compliments)
    
    async def deny_pending_compliment(self, index):

        # Get pending compliments
        pending_compliments = await self.get_pending_compliments()

        # Remove compliment
        pending_compliments.pop(index)

        # Set pending compliments
        await self.set_pending_compliments(pending_compliments)
    
    async def get_compliments(self):

        # Get compliment data
        compliment_data = await self.get_compliment_data()

        return compliment_data["compliments"]
    
    async def set_compliments(self, compliments):

        # Get compliment data
        compliment_data = await self.get_compliment_data()

        compliment_data["compliments"] = compliments

        # Set compliment data
        await self.set_compliment_data(compliment_data)
    
    async def get_compliment(self, nsfw = False):

        # Get compliments
        compliments = await self.get_compliments()

        while True:
            compliment = choice(compliments)

            if nsfw or "nsfw" not in compliment["tags"]:
                return compliment
