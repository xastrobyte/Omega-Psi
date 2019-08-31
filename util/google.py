import discord
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

from category.globals import loop

from database.database import database

from util.functions import get_embed_color

OMEGA_PSI_TASKLIST = "cnVZakVxNXBIQU5FYWVfMg"
OMEGA_PSI_FILE_CHANGE_TASKLIST = "cVVjY0JQcnJCM1dxT0FJUw"
OMEGA_PSI_UPDATE = "TFZDaXlYSXZUaV82VEJoNg"

SCOPES = [
    "https://www.googleapis.com/auth/tasks"
]

# # # # # # # # # # # # # # # # # # # # # # # # #
# Authentication
# # # # # # # # # # # # # # # # # # # # # # # # #

async def authenticate(ctx, bot):

    # Get Fellow Hashbrown Discord User object
    fellow_hashbrown = bot.get_user(int(os.environ["DISCORD_ME"]))

    # Load the credentials for Omega Psi from the database
    credentials = await database.bot.get_google()

    # Load Fellow Hashbrown's google data from the database
    #   Hopefully in the future, I can get any user's information from their own Google account
    creds = await database.users.get_google(fellow_hashbrown)
    if creds != {}:
        creds = Credentials(
            creds["access_token"],
            refresh_token = creds["refresh_token"],
            token_uri = "https://accounts.google.com/o/oauth2/token",
            client_id = credentials["installed"]["client_id"],
            client_secret = credentials["installed"]["client_secret"]
        )
    else:
        creds = None

    # There are no valid credentials; Refresh them
    if not creds or not creds.valid:

        # Create the flow from the credentials
        flow = Flow.from_client_config(
            credentials, 
            scopes = SCOPES,
            redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
        )

        # Retrieve the url for authorization and ask the user to visit the webpage
        auth_url, _ = flow.authorization_url(prompt = "consent")
        await fellow_hashbrown.send(
            embed = discord.Embed(
                title = "Authenticate through Google",
                description = "Visit [this link]({}) to authenticate yourself through your Google account!".format(auth_url),
                colour = await get_embed_color(ctx.author)
            )
        )

        # Ask the user to enter in the code
        def check(message):
            return (
                message.author.id == fellow_hashbrown.id and
                message.channel.recipient.id == fellow_hashbrown.id
            )
        message = await bot.wait_for("message", check = check)

        # Fetch the token from Google and save the new credentials into the user's entry in the database
        flow.fetch_token(code = message.content)
        creds = flow.credentials
        await database.users.set_google(
            ctx.author,
            {
                "valid": creds.valid,
                "expired": creds.expired,
                "refresh_token": creds.refresh_token,
                "access_token": creds.token
            }
        )
    
    return creds

# # # # # # # # # # # # # # # # # # # # # # # # #
# Tasks (TODO) List
# # # # # # # # # # # # # # # # # # # # # # # # #
    
async def get_tasks(ctx, bot):

    # Authenticate if needed
    creds = await authenticate(ctx, bot)

    # Call the Tasks API
    service = build("tasks", "v1", credentials = creds)
    api_call = service.tasks().list(tasklist = OMEGA_PSI_TASKLIST)
    results = await loop.run_in_executor(None,
        api_call.execute
    )
    items = sorted(results.get("items", []), key = lambda item: item["position"])

    return items

async def add_task(ctx, bot, task):

    # Authenticate if needed
    creds = await authenticate(ctx, bot)

    # Call the Tasks API
    service = build("tasks", "v1", credentials = creds)
    api_call = service.tasks().insert(
        tasklist = OMEGA_PSI_TASKLIST,
        body = {
            "title": task
        }
    )
    await loop.run_in_executor(None,
        api_call.execute
    )

    return True

async def remove_task(ctx, bot, task_number):
    
    # Get a list of tasks; Find the task with the given task number as a position
    tasks = await get_tasks(ctx, bot)
    task = None
    for item in tasks:
        if item["position"].endswith(str(task_number - 1)):
            task = item
            break
    
    # Check if there was a task found
    if task:

        # Authenticate the user if needed
        creds = await authenticate(ctx, bot)

        # Call the Tasks API
        service = build("tasks", "v1", credentials = creds)
        api_call = service.tasks().delete(
            tasklist = OMEGA_PSI_TASKLIST,
            task = item["id"]
        )
        await loop.run_in_executor(None,
            api_call.execute
        )

        return task["title"]
    
    return False

# # # # # # # # # # # # # # # # # # # # # # # # #
# Remember Files
# # # # # # # # # # # # # # # # # # # # # # # # #

async def get_files(ctx, bot):

    # Authenticate if needed
    creds = await authenticate(ctx, bot)

    # Call the tasks API
    service = build("tasks", "v1", credentials = creds)
    api_call = service.tasks().list(
        tasklist = OMEGA_PSI_FILE_CHANGE_TASKLIST
    )
    results = await loop.run_in_executor(None,
        api_call.execute
    )
    items = results.get("items", [])
    parent_items = [item for item in items if "parent" not in item]
    child_items = [item for item in items if "parent" in item]

    # Get the basics of the items and add subtasks
    items = []
    item_ids = {}
    count = 0

    # Add parent items first
    for item in parent_items:
        item_ids[item["id"]] = count
        items.append({
            "title": item["title"],
            "id": item["id"],
            "items": []
        })
        count += 1
    
    # Add child items
    for item in child_items:
        items[item_ids[item["parent"]]]["items"].append({
            "title": item["title"]
        })

    return items

async def add_file(ctx, bot, filename, reason):

    # Get the existing files to see if the filename already exists
    items = await get_files(ctx, bot)
    task = None
    for item in items:
        print(item["title"], filename, item["title"] == filename)
        if item["title"] == filename:
            task = item
            break
    
    # Authenticate if needed
    creds = await authenticate(ctx, bot)

    # Call the tasks API to add the reason as a subtask to the filename task
    service = build("tasks", "v1", credentials = creds)

    # Check if the filename as a task already exists
    if task:

        # Insert the task
        api_call = service.tasks().insert(
            tasklist = OMEGA_PSI_FILE_CHANGE_TASKLIST,
            body = {
                "title": reason
            }
        )
        results = await loop.run_in_executor(None,
            api_call.execute
        )

        # Move the task to the parent task
        api_call = service.tasks().move(
            tasklist = OMEGA_PSI_FILE_CHANGE_TASKLIST,
            task = results["id"],
            parent = task["id"]
        )
        results = await loop.run_in_executor(None,
            api_call.execute
        )

        return results["title"]
    
    # The filename as a task does not exist, create a new one. then add the subtask
    else:

        # Create the new filename task
        api_call = service.tasks().insert(
            tasklist = OMEGA_PSI_FILE_CHANGE_TASKLIST,
            body = {
                "title": filename
            }
        )
        results = await loop.run_in_executor(None,
            api_call.execute
        )
        return await add_file(ctx, bot, filename, reason)
    
    return None

async def clear_files(ctx, bot):

    # Authenticate if needed
    creds = await authenticate(ctx, bot)

    # Call the tasks API
    service = build("tasks", "v1", credentials = creds)
    api_call = service.tasks().clear(tasklist = OMEGA_PSI_FILE_CHANGE_TASKLIST)
    await loop.run_in_executor(None,
        api_call.execute
    )

# # # # # # # # # # # # # # # # # # # # # # # # #
# Pending Update
# # # # # # # # # # # # # # # # # # # # # # # # #

async def create_pending_update(ctx, bot):

    # Authenticate if needed
    creds = await authenticate(ctx, bot)

    # Call the tasks API
    service = build("tasks", "v1", credentials = creds)
    tasks = ["Features", "Fixes"]
    for task in tasks:
        api_call = service.tasks().insert(
            tasklist = OMEGA_PSI_UPDATE,
            body = {
                "title": task
            }
        )
        await loop.run_in_executor(None,
            api_call.execute
        )

async def get_pending_update(ctx, bot):

    # Authenticate if needed
    creds = await authenticate(ctx, bot)

    # Call the tasks API
    service = build("tasks", "v1", credentials = creds)
    api_call = service.tasks().list(tasklist = OMEGA_PSI_UPDATE)
    results = await loop.run_in_executor(None,
        api_call.execute
    )
    items = results.get("items", [])
    return items

async def commit_pending_update(ctx, bot, version, description):
    features = await get_features(ctx, bot)
    fixes = await get_fixes(ctx, bot)

    # Commit the update to the database
    await database.bot.commit_pending_update(version, description, features, fixes)
    
    # Authenticate if needed
    creds = await authenticate(ctx, bot)

    # Call the tasks API
    service = build("tasks", "v1", credentials = creds)
    api_call = service.tasks().clear(tasklist = OMEGA_PSI_UPDATE)
    await loop.run_in_executor(None,
        api_call.execute
    )

async def get_features(ctx, bot):
    items = await get_pending_update(ctx, bot)
    child_items = [item for item in items if "parent" in item]

    # Find the ID of the Features task
    features_task = None
    for item in items:
        if item["title"] == "Features":
            features_task = item["id"]
            break
    
    # Get a list of all the features
    features = [
        item["title"]
        for item in child_items
        if item["parent"] == features_task
    ]
    return features

async def get_fixes(ctx, bot):
    items = await get_pending_update(ctx, bot)
    child_items = [item for item in items if "parent" in item]

    # Find the ID of the Fixes task
    fixes_task = None
    for item in items:
        if item["title"] == "Fixes":
            fixes_task = item["id"]
            break
    
    # Get a list of all the fixes
    fixes = [
        item["title"]
        for item in child_items
        if item["parent"] == fixes_task
    ]
    return fixes

async def add_feature(ctx, bot, feature):
    items = await get_pending_update(ctx, bot)

    # Find the ID of the Features task
    features_task = None
    for item in items:
        if item["title"] == "Features":
            features_task = item["id"]
            break
    
    # Authenticate if needed
    creds = await authenticate(ctx, bot)

    # Insert the feature as a task
    service = build("tasks", "v1", credentials = creds)
    api_call = service.tasks().insert(
        tasklist = OMEGA_PSI_UPDATE,
        body = {
            "title": feature
        }
    )
    results = await loop.run_in_executor(None,
        api_call.execute
    )

    # Move the feature underneath the Features task
    api_call = service.tasks().move(
        tasklist = OMEGA_PSI_UPDATE,
        task = results["id"],
        parent = features_task
    )
    await loop.run_in_executor(None,
        api_call.execute
    )

async def add_fix(ctx, bot, fix):
    items = await get_pending_update(ctx, bot)

    # Find the ID of the Fixes task
    fixes_task = None
    for item in items:
        if item["title"] == "Fixes":
            fixes_task = item["id"]
            break
    
    # Authenticate if needed
    creds = await authenticate(ctx, bot)

    # Insert the fix as a task
    service = build("tasks", "v1", credentials = creds)
    api_call = service.tasks().insert(
        tasklist = OMEGA_PSI_UPDATE,
        body = {
            "title": fix
        }
    )
    results = await loop.run_in_executor(None,
        api_call.execute
    )

    # Move the feature underneath the Fixes task
    api_call = service.tasks().move(
        tasklist = OMEGA_PSI_UPDATE,
        task = results["id"],
        parent = fixes_task
    )
    await loop.run_in_executor(None,
        api_call.execute
    )