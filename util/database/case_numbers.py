from datetime import datetime
from discord import User
from functools import partial
from typing import Union

from cogs.globals import loop

from util.string import datetime_to_dict


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class CaseNumber:
    def __init__(self, case_numbers):
        self._case_numbers = case_numbers

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Suggestion Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_suggestion_cases_sync(self, *, key=None):
        """Synchronously retrieves all the suggestion cases that have been submitted

        :param key: A function that filters out suggestions
            The function should only take in one parameter: the suggestion case

        :returns: A JSON object of suggestion cases
        """

        # Default
        default = {
            "_id": "suggestions",
            "number": 1,
            "cases": {}
        }

        # Get suggestion data
        suggestion_data = self._case_numbers.find_one({"_id": "suggestions"})
        if suggestion_data is None:
            self.set_suggestion_cases_sync(default, insert=True)
            suggestion_data = self.get_suggestion_cases_sync(key=key)

        # Check if there is a filter
        if key is not None:
            filtered = {}
            for case in suggestion_data["cases"]:
                if key(suggestion_data["cases"][case]):
                    filtered[case] = suggestion_data["cases"][case]
            return {
                "number": suggestion_data["number"],
                "cases": filtered
            }
        return suggestion_data

    def set_suggestion_cases_sync(self, suggestion_cases, *, insert=False):
        """Synchronously sets the suggestion case data

        :param suggestion_cases: A JSON object of suggestion cases
        :param insert: Whether to insert or update into the database (Default: False)
        """
        if insert:
            self._case_numbers.insert_one(suggestion_cases)
        else:
            self._case_numbers.update_one(
                {"_id": "suggestions"},
                {"$set": suggestion_cases},
                upsert=False)

    def get_suggestion_number_sync(self):
        """Synchronously retrieves the current suggestion case number

        :returns: The current suggestion case number
        """
        suggestion_data = self.get_suggestion_cases_sync()
        return suggestion_data["number"]

    def add_suggestion_sync(self, submitter: Union[User, str], suggestion, message_id: Union[int, str]):
        """Synchronously adds a new suggestion

        :param submitter: The Discord User who submitted the suggestion
        :param suggestion: The suggestion
        :param message_id: The ID of the message sent to the suggestion channel
        """
        suggestion_data = self.get_suggestion_cases_sync()

        # Get the current number and then update it
        number = suggestion_data["number"]
        suggestion_data["number"] += 1

        # Add the suggestion
        suggestion_data["cases"][str(number)] = {
            "suggestion": suggestion,
            "author": submitter if isinstance(submitter, str) else str(submitter.id),
            "time": datetime_to_dict(datetime.now()),
            "message_id": str(message_id),
            "seen": None,
            "consideration": None
        }
        self.set_suggestion_cases_sync(suggestion_data)

    def get_suggestion_sync(self, suggestion_number):
        """Synchronously retrieves the suggestion associated with the specified number

        :param suggestion_number: The suggestion case number to get

        :returns: The suggestion case associated with the specified number, or None if not found.
        """
        suggestion_data = self.get_suggestion_cases_sync()
        if str(suggestion_number) in suggestion_data["cases"]:
            return suggestion_data["cases"][str(suggestion_number)]
        return None

    def mark_suggestion_seen_sync(self, suggestion_number, developer: Union[User, str]):
        """Synchronously marks the suggestion associated with the specified number as seen

        :param suggestion_number: The suggestion case number to mark as seen
        :param developer: The developer who marked the suggestion case as seen
        """
        suggestion_data = self.get_suggestion_cases_sync()
        if str(suggestion_number) in suggestion_data["cases"]:
            suggestion_data["cases"][str(suggestion_number)]["seen"] = developer if isinstance(developer, str) else str(
                developer.id)
            self.set_suggestion_cases_sync(suggestion_data)

    def consider_suggestion_sync(self, suggestion_number, considered, reason=None):
        """Synchronously considers the suggestion associated with the specified number

        :param suggestion_number: The suggestion case number to consider
        :param considered: Whether or not the suggestion is being considered
        :param reason: The reason why the suggestion is not considered
            Note: the reason parameter is only used if considered == False
        """
        suggestion_data = self.get_suggestion_cases_sync()
        if str(suggestion_number) in suggestion_data["cases"]:
            consideration = {
                "considered": considered
            }
            if not considered:
                consideration["reason"] = reason
            suggestion_data["cases"][str(suggestion_number)]["consideration"] = consideration
            self.set_suggestion_cases_sync(suggestion_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_suggestion_cases(self, *, key=None):
        """Asynchronously retrieves all the suggestion cases that have been submitted

        :param key: A function that filters out suggestions

        :returns: A JSON object of suggestion cases
        """
        return await loop.run_in_executor(None, partial(self.get_suggestion_cases_sync, key=key))

    async def set_suggestion_cases(self, suggestion_cases):
        """Asynchronously sets the suggestion case data

        :param suggestion_cases: A JSON object of suggestion cases
        """
        await loop.run_in_executor(None, self.set_suggestion_cases_sync, suggestion_cases)

    async def get_suggestion_number(self):
        """Asynchronously retrieves the current suggestion case number

        :returns: The current suggestion case number
        """
        return await loop.run_in_executor(None, self.get_suggestion_number_sync)

    async def add_suggestion(self, submitter: Union[User, str], suggestion, message_id):
        """Asynchronously adds a new suggestion

        :param submitter: The Discord User who submitted the suggestion
        :param suggestion: The suggestion
        :param message_id: The ID of the message sent to the suggestion channel
        """
        await loop.run_in_executor(None, self.add_suggestion_sync, submitter, suggestion, message_id)

    async def get_suggestion(self, suggestion_number):
        """Asynchronously retrieves the suggestion associated with the specified number

        :param suggestion_number: The suggestion case number to get

        :returns: The suggestion case associated with the specified number, or None if not found.
        """
        return await loop.run_in_executor(None, self.get_suggestion_sync, suggestion_number)

    async def mark_suggestion_seen(self, suggestion_number, developer: Union[User, str]):
        """Asynchronously marks the suggestion associated with the specified number as seen

        :param suggestion_number: The suggestion case number to mark as seen
        :param developer: The developer who marked the suggestion case as seen
        """
        await loop.run_in_executor(None, self.mark_suggestion_seen_sync, suggestion_number, developer)

    async def consider_suggestion(self, suggestion_number, considered, reason=None):
        """Asynchronously considers the suggestion associated with the specified number

        :param suggestion_number: The suggestion case number to consider
        :param considered: Whether or not the suggestion is being considered
        :param reason: The reason why the suggestion is not considered
            Note: the reason parameter is only used if considered == False
        """
        await loop.run_in_executor(None, self.consider_suggestion_sync, suggestion_number, considered, reason)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Bug Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_bug_cases_sync(self, *, key=None):
        """Synchronously retrieves all the bug cases that have been reported

        :param key: A function that filters out bugs

        :returns: A JSON object of bug cases
        """

        # Default
        default = {
            "_id": "bugs",
            "number": 1,
            "cases": {}
        }

        # Get bug data
        bug_data = self._case_numbers.find_one({"_id": "bugs"})
        if bug_data is None:
            self.set_bug_cases_sync(default, insert=True)
            bug_data = self.get_bug_cases_sync(key=key)

        # Check if there is a filter
        if key is not None:
            filtered = {}
            for case in bug_data["cases"]:
                if key(bug_data["cases"][case]):
                    filtered[case] = bug_data["cases"][case]
            return {
                "number": bug_data["number"],
                "cases": filtered
            }
        return bug_data

    def set_bug_cases_sync(self, bug_cases, *, insert=False):
        """Synchronously sets the bug case data

        :param bug_cases: A JSON object of bug cases
        :param insert: Whether to insert or update into the database (Default: False)
        """
        if insert:
            self._case_numbers.insert_one(bug_cases)
        else:
            self._case_numbers.update_one(
                {"_id": "bugs"},
                {"$set": bug_cases},
                upsert=False)

    def get_bug_number_sync(self):
        """Synchronously retrieves the current bug case number

        :returns: The current bug case number
        """
        bug_data = self.get_bug_cases_sync()
        return bug_data["number"]

    def add_bug_sync(self, source_type, source, reporter: Union[User, str], bug_description, message_id):
        """Synchronously adds a new bug

        :param source_type: The type of source of the bug, either website or bot
        :param source: The specific source of the bug
        :param reporter: The Discord User who reported the bug
        :param bug_description: A description of the bug itself
        :param message_id: The ID of the message sent to the Bug Channel
        """
        bug_data = self.get_bug_cases_sync()

        # Get the current number and then update it
        number = bug_data["number"]
        bug_data["number"] += 1

        # Add the bug
        bug_data["cases"][str(number)] = {
            "bug": bug_description,
            "source_type": source_type,
            "source": source,
            "author": reporter if isinstance(reporter, str) else str(reporter.id),
            "time": datetime_to_dict(datetime.now()),
            "message_id": str(message_id),
            "seen": None,
            "fixed": False
        }
        self.set_bug_cases_sync(bug_data)

    def get_bug_sync(self, bug_number):
        """Synchronously retrieves the bug associated with the specified number

        :param bug_number: The bug case number to get

        :returns: The bug case associated with the specified number, or None if not found
        """
        bug_data = self.get_bug_cases_sync()
        if str(bug_number) in bug_data["cases"]:
            return bug_data["cases"][str(bug_number)]
        return None

    def mark_bug_seen_sync(self, bug_number, developer: Union[User, str]):
        """Synchronously marks the bug associated with the specified number as seen

        :param bug_number: The bug case number to mark as seen
        :param developer: The developer who marked the bug case as seen
        """
        bug_data = self.get_bug_cases_sync()
        if str(bug_number) in bug_data["cases"]:
            bug_data["cases"][str(bug_number)]["seen"] = developer if isinstance(developer, str) else str(developer.id)
            self.set_bug_cases_sync(bug_data)

    def fix_bug_sync(self, bug_number):
        """Synchronously marks the bug associated with the specified number as fixed

        :param bug_number: The bug case number to mark as fixed
        """
        bug_data = self.get_bug_cases_sync()
        if str(bug_number) in bug_data["cases"]:
            bug_data["cases"][str(bug_number)]["fixed"] = True
            self.set_bug_cases_sync(bug_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_bug_cases(self, *, key=None):
        """Asynchronously retrieves all the bug cases that have been reported

        :param key: A function that filters out bugs

        :returns: A JSON object of bug cases
        """
        return await loop.run_in_executor(None, partial(self.get_bug_cases_sync, key=key))

    async def set_bug_cases(self, bug_cases):
        """Asynchronously sets the bug case data

        :param bug_cases: A JSON object of bug cases
        """
        await loop.run_in_executor(None, self.set_bug_cases_sync, bug_cases)

    async def get_bug_number(self):
        """Asynchronously retrieves the current bug case number

        :returns: The current bug case number
        """
        return await loop.run_in_executor(None, self.get_bug_number_sync)

    async def add_bug(self, source_type, source, reporter: Union[User, str], bug_description, message_id):
        """Asynchronously adds a new bug

        :param source_type: The type of source of the bug, either website or bot
        :param source: The specific source of the bug
        :param reporter: The Discord User who reported the bug
        :param bug_description: A description of the bug itself
        :param message_id: The ID of the message sent to the Bug Channel
        """
        await loop.run_in_executor(None, self.add_bug_sync, source_type, source, reporter, bug_description, message_id)

    async def get_bug(self, bug_number):
        """Asynchronously retrieves the bug associated with the specified number

        :param bug_number: The bug case number to get

        :returns: The bug case associated with the specified number, or None if not found
        """
        return await loop.run_in_executor(None, self.get_bug_sync, bug_number)

    async def mark_bug_seen(self, bug_number, developer: Union[User, str]):
        """Asynchronously marks the bug associated with the specified number as seen

        :param bug_number: The bug case number to mark as seen
        :param developer: The developer who marked the bug case as seen
        """
        await loop.run_in_executor(None, self.mark_bug_seen_sync, bug_number, developer)

    async def fix_bug(self, bug_number):
        """Asynchronously marks the bug associated with the specified number as fixed

        :param bug_number: The bug case number to mark as fixed
        """
        await loop.run_in_executor(None, self.fix_bug_sync, bug_number)
