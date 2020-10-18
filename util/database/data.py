from discord import User
from random import choice
from typing import Union

from cogs.globals import loop


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Data:
    def __init__(self, data):
        self._data = data

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Flask Session Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_session_user(self, user_id):
        """Retrieves the user that the session ID is linked to

        Parameters
        ----------
            user_id : str
                The ID of the user to get the stored data of
        
        Returns
        -------
            dict
                The JSON object of the user's session data
        """

        session_data = self._data.find_one({"_id": user_id})
        if session_data is None:
            self.set_session_user(user_id, {}, insert=True)
            session_data = self.get_session_user(user_id)
        return session_data

    def set_session_user(self, user_id, session_data, *, insert=False):
        """Sets the user that the specified session ID is linked to

        Parameters
        ----------
            user_id : str   
                The ID of the user to set the stored data for
            session_data : dict
                The JSON object of the user's session data to store
        """
        if insert:
            session_data["_id"] = user_id
            self._data.insert_one(session_data)
        else:
            self._data.update_one(
                {"_id": user_id},
                {"$set": session_data},
                upsert=False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Insult Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_insult_data_sync(self):
        """Synchronously retrieves the insult data from the database

        Returns
        -------
            dict
                The JSON object of the pending insults and insults
        """

        # Default
        default = {
            "_id": "insults",
            "pending_insults": [],
            "insults": []
        }

        # Get insult data
        insult_data = self._data.find_one({"_id": "insults"})
        if insult_data is None:
            self.set_insult_data_sync(default, insert=True)
            insult_data = self.get_insult_data_sync()
        return insult_data

    def set_insult_data_sync(self, insult_data, *, insert=True):
        """Synchronously sets the insult data in the database

        Parameters
        ----------
            insult_data : dict
                The JSON object of the pending insults and insults
        """
        if insert:
            self._data.insert_one(insult_data)
        else:
            self._data.update_one(
                {"_id": "insults"},
                {"$set": insult_data},
                upsert=False)

    def get_insults_sync(self):
        """Synchronously retrieves all insults from the database

        Returns
        -------
            list
                A list of insults in Omega Psi
        """
        insult_data = self.get_insult_data_sync()
        return insult_data["insults"]

    def set_insults_sync(self, insults):
        """Synchronously sets the insults in the database
        
        Parameters
        ----------
            insults : list
                A list of insults to set in Omega Psi
        """
        insult_data = self.get_insult_data_sync()
        insult_data["insults"] = insults
        self.set_insult_data_sync(insult_data)

    def get_pending_insults_sync(self):
        """Synchronously retrieves all pending insults from the database

        Returns
        -------
            list
                A list of pending insults in Omega Psi
        """
        insult_data = self.get_insult_data_sync()
        return insult_data["pending_insults"]

    def set_pending_insults_sync(self, pending_insults):
        """Synchronously sets the pending insults in the database

        Parameters
        ----------
            pending_insults : list
                A list of pending insults to set in Omega Psi
        """
        insult_data = self.get_insult_data_sync()
        insult_data["pending_insults"] = pending_insults
        self.set_insult_data_sync(insult_data)

    def add_pending_insult_sync(self, insult, author: Union[User, str]):
        """Synchronously adds a new pending insult to the database
        
        Parameters
        ----------
            insult : str
                The insult to add to the pending insults
            author : str or User
                The author who requested the pending insult to be added
        """
        pending_insults = self.get_pending_insults_sync()
        pending_insults.append({
            "insult": insult,
            "author": author if isinstance(author, str) else str(author.id),
            "tags": []
        })
        self.set_pending_insults_sync(pending_insults)

    def add_pending_insult_tags_sync(self, index, tags=None):
        """Synchronously adds tags to an existing pending insult in the database

        Parameters
        ----------
            index : int
                The insult index to add the specified tags to
            tags : list
                A list of tags to set for the specified insult
        """
        if tags is None:
            tags = []
        pending_insults = self.get_pending_insults_sync()
        pending_insults[index]["tags"] += tags
        self.set_pending_insults_sync(pending_insults)

    def approve_pending_insult_sync(self, index):
        """Synchronously approves a pending insult and adds it to the insults in the database

        Parameters
        ----------
            index : int
                The insult index to add to the insults in Omega Psi
        """
        pending_insults = self.get_pending_insults_sync()
        insult = pending_insults.pop(index)
        self.set_pending_insults_sync(pending_insults)

        insults = self.get_insults_sync()
        insults.append(insult)
        self.set_insults_sync(insults)

    def deny_pending_insult_sync(self, index):
        """Synchronously denies a pending insult and removes it from the database

        Parameters
        ----------
            index : int
                The insult index to remove from the pending insults
        """
        pending_insults = self.get_pending_insults_sync()
        pending_insults.pop(index)
        self.set_pending_insults_sync(pending_insults)

    def get_insult_sync(self, nsfw=False):
        """Synchronously retrieves a random insult from the database

        Parameters
        ----------
            nsfw : boolean
                Whether or not to get NSFW insults as well
        
        Returns
        -------
            list
                A list of insults
        """
        insults = self.get_insults_sync()
        while True:
            insult = choice(insults)
            if nsfw or "nsfw" not in insult["tags"]:
                return insult

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_insult_data(self):
        """Asynchronously retrieves the insult data from the database

        Returns
        -------
            dict
                The JSON object of the pending insults and insults
        """
        return await loop.run_in_executor(None, self.get_insult_data_sync)

    async def set_insult_data(self, insult_data):
        """Asynchronously sets the insult data in the database

        Parameters
        ----------
            insult_data : dict
                The JSON object of the pending insults and insults
        """
        await loop.run_in_executor(None, self.set_insult_data_sync, insult_data)

    async def get_insults(self):
        """Asynchronously retrieves all insults from the database

        Returns
        -------
            list
                A list of insults in Omega Psi
        """
        return await loop.run_in_executor(None, self.get_insults_sync)

    async def set_insults(self, insults):
        """Asynchronously sets the insults in the database
        
        Parameters
        ----------
            insults : list
                A list of insults to set in Omega Psi
        """
        await loop.run_in_executor(None, self.set_insults_sync, insults)

    async def get_pending_insults(self):
        """Asynchronously retrieves all pending insults from the database

        Returns
        -------
            list
                A list of pending insults in Omega Psi
        """
        return await loop.run_in_executor(None, self.get_pending_insults_sync)

    async def set_pending_insults(self, pending_insults):
        """Asynchronously sets the pending insults in the database

        Parameters
        ----------
            pending_insults : list
                A list of pending insults to set in Omega Psi
        """
        await loop.run_in_executor(None, self.set_pending_insults_sync, pending_insults)

    async def add_pending_insult(self, insult, author_id):
        """Asynchronously adds a new pending insult to the database
        
        Parameters
        ----------
            insult : str
                The insult to add to the pending insults
            author_id : str or User
                The author who requested the pending insult to be added
        """
        await loop.run_in_executor(None, self.add_pending_insult_sync, insult, author_id)

    async def add_pending_insult_tags(self, index, tags=None):
        """Asynchronously adds tags to an existing pending insult in the database

        Parameters
        ----------
            index : int
                The insult index to add the specified tags to
            tags : list
                A list of tags to set for the specified insult
        """
        if tags is None:
            tags = []
        await loop.run_in_executor(None, self.add_pending_insult_tags_sync, index, tags)

    async def approve_pending_insult(self, index):
        """Asynchronously approves a pending insult and adds it to the insults in the database

        Parameters
        ----------
            index : int
                The insult index to add to the insults in Omega Psi
        """
        await loop.run_in_executor(None, self.approve_pending_insult_sync, index)

    async def deny_pending_insult(self, index):
        """Asynchronously denies a pending insult and removes it from the database

        Parameters
        ----------
            index : int
                The insult index to remove from the pending insults
        """
        await loop.run_in_executor(None, self.deny_pending_insult_sync, index)

    async def get_insult(self, nsfw=False):
        """Asynchronously retrieves a random insult from the database

        Parameters
        ----------
            nsfw : boolean
                Whether or not to get NSFW insults as well
        
        Returns
        -------
            list
                A list of insults
        """
        return await loop.run_in_executor(None, self.get_insult_sync, nsfw)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Compliment Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_compliment_data_sync(self):
        """Synchronously retrieves the compliment data from the database

        Returns
        ----------
            dict
                The JSON object of pending compliments and compliments
        """

        # Default
        default = {
            "pending_compliments": [],
            "compliments": []
        }

        # Get compliment data
        compliment_data = self._data.find_one({"_id": "compliments"})
        if not compliment_data:
            self._data.insert_one({"_id": "compliments"})
            self.set_compliment_data_sync(default)
            compliment_data = default
        return dict(compliment_data)

    def set_compliment_data_sync(self, compliment_data):
        """Synchronously sets the compliment data in the database

        Parameters
        ----------
            compliment_data : dict
                The JSON object of pending compliments and compliments to set
        """
        self._data.update_one({"_id": "compliments"}, {"$set": compliment_data}, upsert=False)

    def get_compliments_sync(self):
        """Synchronously retrieves all compliments from the database

        Returns
        -------
            list
                A list of compliments in Omega Psi
        """
        compliment_data = self.get_compliment_data_sync()
        return compliment_data["compliments"]

    def set_compliments_sync(self, compliments):
        """Synchronously sets the compliments in the database

        Parameters
        ----------
            compliments : list
                A list of compliments to set in Omega Psi
        """
        compliment_data = self.get_compliment_data_sync()
        compliment_data["compliments"] = compliments
        self.set_compliment_data_sync(compliment_data)

    def get_pending_compliments_sync(self):
        """Synchronously retrieves all pending compliments from the database

        Returns
        -------
            list
                A list of pending compliments in Omega Psi
        """
        compliment_data = self.get_compliment_data_sync()
        return compliment_data["pending_compliments"]

    def set_pending_compliments_sync(self, pending_compliments):
        """Synchronously sets the pending compliments in the database

        Parameters
        ----------
            pending_compliments : list
                A list of pending compliments to set in Omega Psi
        """
        compliment_data = self.get_compliment_data_sync()
        compliment_data["pending_compliments"] = pending_compliments
        self.set_compliment_data_sync(compliment_data)

    def add_pending_compliment_sync(self, compliment, author: Union[User, str]):
        """Synchronously adds a new pending compliment to the database

        Parameters
        ----------
            compliment : str
                The compliment to add to the pending compliments
            author : str or User
                The author who requested the compliment to be added
        """
        pending_compliments = self.get_pending_compliments_sync()
        pending_compliments.append({
            "compliment": compliment,
            "author": author if isinstance(author, str) else str(author.id),
            "tags": []
        })
        self.set_pending_compliments_sync(pending_compliments)

    def add_pending_compliment_tags_sync(self, index, tags=None):
        """Synchronously adds tags to an existing pending compliment in the database

        Parameters
        ----------
            index : int
                The compliment index to add the specified tags to
            tags : list
                The list of tags to add to the specified compliment
        """
        if tags is None:
            tags = []
        pending_compliments = self.get_pending_compliments_sync()
        pending_compliments[index]["tags"] += tags
        self.set_pending_compliments_sync(pending_compliments)

    def approve_pending_compliment_sync(self, index):
        """Synchronously approves a pending compliment and adds it to the compliments in the database

        Parameters
        ----------
            index : int
                The compliment index to add to the compliments in Omega Psi
        """
        pending_compliments = self.get_pending_compliments_sync()
        compliment = pending_compliments.pop(index)
        self.set_pending_compliments_sync(pending_compliments)

        compliments = self.get_compliments_sync()
        compliments.append(compliment)
        self.set_compliments_sync(compliments)

    def deny_pending_compliment_sync(self, index):
        """Synchronously denies a pending compliment and removes it from the database

        Parameters
        ----------
            index : int
                The compliment index to remove from the pending compliments
        """
        pending_compliments = self.get_pending_compliments_sync()
        pending_compliments.pop(index)
        self.set_pending_compliments_sync(pending_compliments)

    def get_compliment_sync(self, nsfw=False):
        """Synchronously retrieves a random compliment from the database

        Parameters
        ----------
            nsfw : boolean
                Whether or not to get NSFW compliments as well
        
        Returns
        -------
            list
                A list of compliments
        """
        compliments = self.get_compliments_sync()
        while True:
            compliment = choice(compliments)
            if nsfw or "nsfw" not in compliment["tags"]:
                return compliment

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_compliment_data(self):
        """Asynchronously retrieves the compliment data from the database

        Returns
        ----------
            dict
                The JSON object of pending compliments and compliments
        """
        return await loop.run_in_executor(None, self.get_compliment_data_sync)

    async def set_compliment_data(self, compliment_data):
        """Asynchronously sets the compliment data in the database

        Parameters
        ----------
            compliment_data : dict
                The JSON object of pending compliments and compliments to set
        """
        await loop.run_in_executor(None, self.set_compliment_data_sync, compliment_data)

    async def get_compliments(self):
        """Asynchronously retrieves all compliments from the database

        Returns
        -------
            list
                A list of compliments in Omega Psi
        """
        return await loop.run_in_executor(None, self.get_compliments_sync)

    async def set_compliments(self, compliments):
        """Asynchronously sets the compliments in the database

        Parameters
        ----------
            compliments : list
                A list of compliments to set in Omega Psi
        """
        await loop.run_in_executor(None, self.set_compliments_sync, compliments)

    async def get_pending_compliments(self):
        """Asynchronously retrieves all pending compliments from the database

        Returns
        -------
            list
                A list of pending compliments in Omega Psi
        """
        return await loop.run_in_executor(None, self.get_pending_compliments_sync)

    async def set_pending_compliments(self, pending_compliments):
        """Asynchronously sets the pending compliments in the database

        Parameters
        ----------
            pending_compliments : list
                A list of pending compliments to set in Omega Psi
        """
        await loop.run_in_executor(None, self.set_pending_compliments_sync, pending_compliments)

    async def add_pending_compliment(self, compliment, author_id):
        """Asynchronously adds a new pending compliment to the database

        Parameters
        ----------
            compliment : str
                The compliment to add to the pending compliments
            author_id : str or User
                The author who requested the compliment to be added
        """
        await loop.run_in_executor(None, self.add_pending_compliment_sync, compliment, author_id)

    async def add_pending_compliment_tags(self, index, tags=None):
        """Asynchronously adds tags to an existing pending compliment in the database

        Parameters
        ----------
            index : int
                The compliment index to add the specified tags to
            tags : list
                The list of tags to add to the specified compliment
        """
        if tags is None:
            tags = []
        await loop.run_in_executor(None, self.add_pending_compliment_tags_sync, index, tags)

    async def approve_pending_compliment(self, index):
        """Asynchronously approves a pending compliment and adds it to the compliments in the database

        Parameters
        ----------
            index : int
                The compliment index to add to the compliments in Omega Psi
        """
        await loop.run_in_executor(None, self.approve_pending_compliment_sync, index)

    async def deny_pending_compliment(self, index):
        """Asynchronously denies a pending compliment and removes it from the database

        Parameters
        ----------
            index : int
                The compliment index to remove from the pending compliments
        """
        await loop.run_in_executor(None, self.deny_pending_compliment_sync, index)

    async def get_compliment(self, nsfw=False):
        """Asynchronously retrieves a random compliment from the database

        Parameters
        ----------
            nsfw : boolean
                Whether or not to get NSFW compliments as well
        
        Returns
        -------
            list
                A list of compliments
        """
        return await loop.run_in_executor(None, self.get_compliment_sync, nsfw)
