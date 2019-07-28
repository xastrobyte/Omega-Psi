from datetime import datetime
from functools import partial

from category.globals import loop

from util.string import datetime_to_dict

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class CaseNumber:
    def __init__(self, case_numbers):
        self._case_numbers = case_numbers
    
    def get_suggestion_cases_sync(self):

        default = {
            "number": 1,
            "cases": {}
        }

        # Get suggestion data
        case_data = self._case_numbers.find_one({"_id": "suggestions"})

        if case_data == None:
            self.set_suggestion_cases_sync(default)
            case_data = default
        
        return case_data
    
    def set_suggestion_cases_sync(self, cases):

        # Check if there is None; create it
        suggestion_data = self._case_numbers.find_one({"_id": "suggestions"})

        if suggestion_data == None:
            self._case_numbers.insert_one({"_id": "suggestions"})
        
        # Set data
        self._case_numbers.update_one(
            {"_id": "suggestions"},
            {"$set": cases},
            upsert = False
        )
    
    def get_suggestion_number_sync(self):
        suggestion_cases = self.get_suggestion_cases_sync()

        return suggestion_cases["number"]
    
    def add_suggestion_sync(self, suggestion, author, email):
        
        # Get suggestion cases
        suggestion_cases = self.get_suggestion_cases_sync()

        # Get current number then update it
        number = suggestion_cases["number"]
        suggestion_cases["number"] += 1

        # Add the suggestion
        current_time = datetime_to_dict(datetime.now())
        suggestion_cases["cases"][str(number)] = {
            "suggestion": suggestion,
            "author": author,
            "email": email,     # This is only set in the sync version of the function
                                # because it is used for the website version of the command
                                # that uses it
            "time": current_time,
            "seen": False
        }

        # Set suggestion cases
        self.set_suggestion_cases_sync(suggestion_cases)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_bug_cases_sync(self):

        default = {
            "number": 1,
            "cases": {}
        }

        # Get bug data
        case_data = self._case_numbers.find_one({"_id": "bugs"})

        if case_data == None:
            self.set_bug_cases_sync(default)
            case_data = default
        
        return case_data
    
    def set_bug_cases_sync(self, cases):

        # Check if there is None; create it
        bug_data = self._case_numbers.find_one({"_id": "bugs"})

        if bug_data == None:
            self._case_numbers.insert_one({"_id": "bugs"})
        
        # Set data
        self._case_numbers.update_one(
            {"_id": "bugs"},
            {"$set": cases},
            upsert = False
        )
    
    def get_bug_number_sync(self):
        bug_cases = self.get_bug_cases_sync()

        return bug_cases["number"]
    
    def add_bug_sync(self, bug, author, email):
        
        # Get bug cases
        bug_cases = self.get_bug_cases_sync()

        # Get current number then update it
        number = bug_cases["number"]
        bug_cases["number"] += 1

        # Add the bug
        current_time = datetime_to_dict(datetime.now())
        bug_cases["cases"][str(number)] = {
            "bug": bug,
            "author": author,
            "email": email,     # This is only set in the sync version of the function
                                # because it is used for the website version of the command
                                # that uses it
            "time": current_time,
            "seen": False
        }

        # Set bug cases
        self.set_bug_cases_sync(bug_cases)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_suggestion_cases(self):

        default = {
            "number": 1,
            "cases": {}
        }
        
        # Get suggestion data
        case_data = await loop.run_in_executor(None,
            self._case_numbers.find_one,
            {"_id": "suggestions"}
        )

        if case_data == None:
            await self.set_suggestion_cases(default)
            case_data = default
        
        return case_data
    
    async def set_suggestion_cases(self, cases):

        # Check if there is None; Create it
        suggestion_data = await loop.run_in_executor(None,
            self._case_numbers.find_one,
            {"_id": "suggestions"}
        )
        if suggestion_data == None:
            await loop.run_in_executor(None,
                self._case_numbers.insert_one,
                {"_id": "suggestions"}
            )
        
        # Set data
        await loop.run_in_executor(None,
            partial(
                self._case_numbers.update_one,
                {"_id": "suggestions"},
                {"$set": cases},
                upsert = False
            )
        )
    
    async def get_suggestion(self, number):
        
        # Get suggestion cases
        suggestion_cases = await self.get_suggestion_cases()

        if str(number) in suggestion_cases:
            return suggestion_cases[str(number)]
        return None
    
    async def get_suggestion_number(self):

        suggestion_cases = await self.get_suggestion_cases()

        return suggestion_cases["number"]
    
    async def mark_suggestion_seen(self, number):

        # Get suggestions cases
        suggestion_cases = await self.get_suggestion_cases()

        suggestion_cases["cases"][str(number)]["seen"] = True

        # Set suggestion cases
        await self.set_suggestion_cases(suggestion_cases)
    
    async def add_suggestion(self, suggestion, author):
        
        # Get suggestion cases
        suggestion_cases = await self.get_suggestion_cases()

        # Get current number then update it
        number = suggestion_cases["number"]
        suggestion_cases["number"] += 1

        # Add the suggestion
        current_time = datetime_to_dict(datetime.now())
        suggestion_cases["cases"][str(number)] = {
            "suggestion": suggestion,
            "author": author,
            "time": current_time,
            "seen": False
        }

        # Set suggestion cases
        await self.set_suggestion_cases(suggestion_cases)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_bug_cases(self):
        
        default = {
            "number": 1,
            "cases": {}
        }
        
        # Get bug data
        case_data = await loop.run_in_executor(None,
            self._case_numbers.find_one,
            {"_id": "bugs"}
        )

        if case_data == None:
            await self.set_bug_cases(default)
            case_data = default
        
        return case_data
    
    async def set_bug_cases(self, cases):

        # Check if there is None; Create it
        bug_data = await loop.run_in_executor(None,
            self._case_numbers.find_one,
            {"_id": "bugs"}
        )
        if bug_data == None:
            await loop.run_in_executor(None,
                self._case_numbers.insert_one,
                {"_id": "bugs"}
            )
        
        # Set data
        await loop.run_in_executor(None,
            partial(
                self._case_numbers.update_one,
                {"_id": "bugs"},
                {"$set": cases},
                upsert = False
            )
        )
    
    async def get_bug(self, number):

        # Get bug cases
        bug_cases = await self.get_bug_cases()

        if str(number) in bug_cases:
            return bug_cases[str(number)]
        return None
    
    async def get_bug_number(self):

        bug_cases = await self.get_bug_cases()

        return bug_cases["number"]
    
    async def mark_bug_seen(self, number):

        # Get bug cases
        bug_cases = await self.get_bug_cases()

        bug_cases["cases"][str(number)]["seen"] = True

        # Set bug cases
        await self.set_bug_cases(bug_cases)
    
    async def add_bug(self, bug, author):

        # Get bug cases
        bug_cases = await self.get_bug_cases()

        # Get current number then update it
        number = bug_cases["number"]
        bug_cases["number"] += 1

        # Add the bug
        current_time = datetime_to_dict(datetime.now())
        bug_cases["cases"][str(number)] = {
            "bug": bug,
            "author": author,
            "time": current_time,
            "seen": False
        }

        # Set bug cases
        await self.set_bug_cases(bug_cases)
