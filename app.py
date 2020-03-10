from asyncio import run_coroutine_threadsafe
from datetime import datetime, timedelta
from discord import Embed
from flask import Flask, session, request, redirect, url_for, render_template, jsonify, make_response, abort
from flask_session import Session
from os import environ
from random import randint
from requests import post, get
from threading import Thread

from cogs.globals import loop, PRIMARY_EMBED_COLOR, MINIGAMES
from cogs.predicates import is_developer_predicate

from util.database.database import database
from util.website.custom_html import get_case_html, get_pending_update_html, get_tasks_html, get_feedback_html, get_user_settings_html, get_server_settings_html
from util.website.page import Page, Section, HomeSection
from util.website.website import Website, Footer, Link

from util.discord import send_webhook_sync
from util.string import dict_to_datetime, datetime_to_string

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

app = Flask("Omega Psi (BETA)")
app.config.update(
    SESSION_TYPE = "mongodb",
    SESSION_MONGODB = database.connection,
    SESSION_MONGODB_DB = "omegapsi",
    SESSION_COOKIE_SECURE = True,
    SESSION_COOKIE_SAMESITE = 'Lax',
    SECRET_KEY = environ["SESSION_SECRET_KEY"],
    PREFERRED_URL_SCHEME = "https",
    PERMANENT_SESSION_LIFETIME = timedelta(days = 7)
)
Session(app)

DISCORD_OAUTH_LINK = "https://discordapp.com/api/oauth2/authorize?client_id=535587516816949248&redirect_uri=https%3A%2F%2Fomegapsi.fellowhashbrown.com%2Flogin&response_type=code&scope=identify"
DISCORD_TOKEN_LINK = "https://discordapp.com/api/oauth2/token"

OMEGA_PSI = None

ALLOW_ORIGIN = "https://omegapsi.fellowhashbrown.com"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.before_request
def make_session_permanent():
    """Makes the current session permanent"""
    request.environ["wsgi.url_scheme"] = "https"

    # Check if the request is made to either /developer or /info
    #   Have the user login
    if request.endpoint in ["developer", "info", "settings"]:
        session["target_url"] = request.endpoint
        cookie_user_id = request.cookies.get("user_id")
        session_user_id = session.get("user_id")
        session["user_id" ] = cookie_user_id if cookie_user_id else session_user_id
        user_data = database.data.get_session_user(session["user_id"])

        # Check if the user is valid
        if user_data and "id" in user_data:

            # Check if their credentials are invalid
            if not("verified_at" in user_data and "expires_in" in user_data and (user_data["verified_at"] + user_data["expires_in"] > int(datetime.now().timestamp()))):
                return redirect(url_for("login")), 302
        
        # The user ID does not exist
        else:
            return redirect(url_for("login")), 302

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Public Routes
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.route("/")
@app.route("/commands")
def commands():
    return render_template("commands.html"), 200

@app.route("/info")
def info():

    # Get the tasks data
    tasks = database.bot.get_tasks_sync()
    if len(tasks) == 0:
        tasks = None
    
    # Get the pending update data
    pending_update = database.bot.get_pending_update_sync()
    if len(pending_update) == 0:
        pending_update = None
    else:
        for feature in pending_update["features"]:
            feature = pending_update["features"][feature]
            feature["datetime"] = datetime_to_string(dict_to_datetime(feature["datetime"]), short = True)
            
    return render_template("info.html", 
        user_id = request.cookies.get("user_id"),
        tasks = tasks,
        pending_update = pending_update
    ), 200

@app.route("/settings")
def settings():

    # Get a list of guilds that Omega Psi and the user are in where the user
    #   also has manage guild permissions
    manageable_guilds = []
    for guild in OMEGA_PSI.guilds:
        member = guild.get_member(int(session.get("user_id")))
        if member and member.guild_permissions.manage_guild:
            manageable_guilds.append(guild)

    # Get the users minigame data from the database
    user_data = database.users.get_user_sync(session.get("user_id"))
    minigames = {}
    for data in user_data:
        if data in MINIGAMES:
            user_data[data].update(
                ratio = round(
                    user_data[data]["won"] / user_data[data]["lost"]
                    if user_data[data]["lost"] > 0 else
                    user_data[data]["won"],
                    2
                )
            )
            minigames[data.replace("_", " ")] = user_data[data]

    return render_template("settings.html", 
        manageable_guilds = manageable_guilds,
        minigames = minigames, 
        user_color = hex(
            user_data["embed_color"]
            if user_data["embed_color"] else
            PRIMARY_EMBED_COLOR
        )[2:]
    ), 200

@app.route("/server/<string:guild_id>")
def server(guild_id):
    
    # Make sure the user can manage the guild and get the 
    #   prefix and disabled commands for the guild
    guild = OMEGA_PSI.get_guild(int(guild_id))
    member = guild.get_member(int(session.get("user_id")))
    if guild and member and member.guild_permissions.manage_guild:
        return render_template("server.html", 
            guild = guild,
            guild_prefix = database.guilds.get_prefix_sync(guild_id),
            disabled_commands = database.guilds.get_disabled_commands_sync(guild_id)
        )
    
    # The guild can't be found or the member can't be found or the member cannot manage the guild
    abort(401)

@app.route("/favicon.ico")
def favicon():
    return redirect("/static/favicon.ico")

@app.route("/privacyPolicy")
def privacy_policy():
    return render_template("privacyPolicy.html"), 200

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Errors
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.errorhandler(404)
def page_not_found(error):
    return render_template("pageNotFound.html"), 404

@app.errorhandler(403)
def missing_access(error):
    return render_template("missingAccess.html"), 403

@app.errorhandler(401)
def not_a_guild_manager(error):
    return render_template("notServerManager.html"), 401

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Feedback Routes
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.route("/reportBug", methods = ["POST", "PUT"])
def report_bug():

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN:

        # Check if the method is POST
        if request.method == "POST":

            # Get the bug report data along with the current user and get
            #   a discord.User object from their ID
            description = request.json["description"]
            user_id = request.cookies.get("user_id")
            user = OMEGA_PSI.get_user(int(user_id))
            case_number = database.case_numbers.get_bug_number_sync()

            # Add the bug report to the database and send an IFTTT webhook to all developers and the Bug channel
            database.case_numbers.add_bug_sync(request.json["sourceType"], request.json["source"], user_id, description)
            embed = Embed(
                title = "Bug Reported (#{})".format(case_number),
                description = "Reported by {}".format(
                    str(user) if user else "Unknown (ID: {})".format(user_id)
                ),
                colour = PRIMARY_EMBED_COLOR
            ).add_field(
                name = "Source",
                value = "`{}` - {}".format(request.json["sourceType"], request.json["source"])
            ).add_field(
                name = "Description",
                value = description,
                inline = False
            )
            send_webhook_sync(environ["BUG_WEBHOOK"], embed)
            for dev in database.bot.get_developers_sync():

                # Send a message to each developer displaying what the bug is
                dev = OMEGA_PSI.get_user(int(dev))
                if dev:
                    developer_send = run_coroutine_threadsafe(
                        dev.send(embed = embed),
                        loop
                    )
                    developer_send.result()
            return jsonify({"message": "Bug #{} created".format(case_number)}), 201
        
        # Check if the method is PUT; A developer has marked a bug as seen
        elif request.method == "PUT":

            # Make sure this user is a developer
            if database.bot.is_developer_sync(session.get("user_id")):
            
                # Get the bug report that is marked as seen
                #   and find the user that reported it
                #   also retrieve the developer that marked the bug as seen
                case_number = request.json["caseNumber"]
                case = database.case_numbers.get_bug_sync(case_number)
                user = OMEGA_PSI.get_user(int(case["author"]))
                dev = OMEGA_PSI.get_user(int(session.get("user_id")))

                # Send a message to the user saying a developer has viewed their bug
                #   only if the user was found and if the bug hasn't been seen already
                if user and not case["seen"]:
                    database.case_numbers.mark_bug_seen_sync(case_number, dev)
                    user_send = run_coroutine_threadsafe(
                        user.send(
                            embed = Embed(
                                title = "Bug Report Seen By Developer",
                                description = "{} has seen your bug report".format(str(dev)),
                                colour = PRIMARY_EMBED_COLOR
                            ).add_field(
                                name = "Bug (#{})".format(case_number),
                                value = case["bug"]
                            )
                        ),
                        loop
                    )
                    user_send.result()
                
                # The bug report was already seen
                #   send an error code for a Swal message to be sent in JS
                elif case["seen"]:
                    return jsonify({"bug": case_number, "developer": str(dev)}), 400
                return jsonify({"message": "Bug #{} marked as seen".format(case_number), "developer": str(dev)}), 201
        
        # The origin does not match ALLOW_ORIGIN
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/suggest", methods = ["POST", "PUT"])
def suggest():

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN:
    
        # Check if the method is POST
        if request.method == "POST":

            # Get the suggestion data along with the current user and get
            #   a discord.User object from their ID
            description = request.json["description"]
            user_id = session.get("user_id")
            user = OMEGA_PSI.get_user(int(user_id))
            case_number = database.case_numbers.get_suggestion_number_sync()

            # Add the bug report to the database and send an IFTTT webhook to all developers
            database.case_numbers.add_suggestion_sync(user_id, description)
            embed = Embed(
                title = "Suggestion (#{})".format(case_number),
                description = "Suggested by {}".format(
                    str(user) if user else "Unknown (ID: {})".format(user_id)
                ),
                colour = PRIMARY_EMBED_COLOR
            ).add_field(
                name = "Description",
                value = description,
                inline = False
            )
            send_webhook_sync(environ["SUGGESTION_WEBHOOK"], embed)
            for dev in database.bot.get_developers_sync():

                # Send a message to each developer displaying what the suggestion is
                dev = OMEGA_PSI.get_user(int(dev))
                if dev:
                    developer_send = run_coroutine_threadsafe(
                        dev.send(embed = embed),
                        loop
                    )
                    developer_send.result()
            return jsonify({"message": "Suggestion #{} created".format(case_number)}), 201
        
        # Check if the method is PUT; A developer has marked a bug as seen
        elif request.method == "PUT":

            # Make sure this user is a developer
            if database.bot.is_developer_sync(session.get("user_id")):
            
                # Get the suggestion that is marked as seen
                #   and find the user that suggested it
                #   also retrieve the developer that marked the suggestion as seen
                case_number = request.json["caseNumber"]
                case = database.case_numbers.get_suggestion_sync(case_number)
                user = OMEGA_PSI.get_user(int(case["author"]))
                dev = OMEGA_PSI.get_user(int(session.get("user_id")))

                # Send a message to the user saying a developer has viewed their suggestion
                #   only if the user was found and if the suggestion hasn't been seen already
                if user and not case["seen"]:
                    database.case_numbers.mark_suggestion_seen_sync(case_number, dev)
                    user_send = run_coroutine_threadsafe(
                        user.send(
                            embed = Embed(
                                title = "Suggestion Seen By Developer",
                                description = "{} has seen your suggestion".format(str(dev)),
                                colour = PRIMARY_EMBED_COLOR
                            ).add_field(
                                name = "Suggestion (#{})".format(case_number),
                                value = case["suggestion"]
                            )
                        ),
                        loop
                    )
                    user_send.result()
                
                # The suggestion was already seen
                #   send an error code for a Swal message to be sent in JS
                elif case["seen"]:
                    return jsonify({"suggestion": case_number, "developer": str(dev)}), 400
                return jsonify({"message": "Suggestion #{} marked as seen".format(case_number)}), 201
    
    # The origin does not match ALLOW_ORIGIN
    return jsonify({"error": "Unauthorized"}), 401

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Settings Routes
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.route("/settings/user", methods = ["POST"])
def settings_user():

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN and session.get("user_id"):

        # Update the user's embed color in the database
        database.users.set_embed_color_sync(session.get("user_id"), int(request.json["userColor"][1:], base = 16))
        return jsonify({"success": True}), 201
    
    # The origin does not match ALLOW_ORIGIN
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/settings/server", methods = ["GET", "POST", "PUT"])
def settings_server():

    # Getting a list of active commands
    if request.method == "GET":
        
        # Get all active commands
        all_commands = []
        disabled_commands = database.guilds.get_disabled_commands_sync(request.args.get("guildID"))
        for command in OMEGA_PSI.walk_commands():

            # Don't add commands that have the is_developer check on it
            if (
                is_developer_predicate not in command.checks and 
                command.qualified_name not in all_commands and
                command.qualified_name not in disabled_commands and
                command.qualified_name != "help"
            ):
                all_commands.append(command.qualified_name)

        return jsonify(all_commands), 200

    else:

        # Only run if the origin is from ALLOW_ORIGIN
        if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN and session.get("user_id"):

            # Updating the prefix
            if request.method == "POST":
                database.guilds.set_prefix_sync(request.json["guildID"], request.json["prefix"])
                return jsonify({"success": True}), 201

            # Enabling/Disabling a command
            elif request.method == "PUT":
                if request.json["enable"]:
                    if database.guilds.enable_command_sync(request.json["guildID"], request.json["command"]):
                        return jsonify({"success": True}), 201
                    return jsonify({"error": "That command is already enabled!"}), 401
                else:
                    if database.guilds.disable_command_sync(request.json["guildID"], request.json["command"]):
                        return jsonify({"success": True}), 201
                    return jsonify({"error": "That command is already disabled!"}), 401
        
        # The origin does not match ALLOW_ORIGIN
        return jsonify({"error": "Unauthorized"}), 401

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Developer Routes
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.route("/login", methods = ["GET", "POST"])
def login():

    # Check if code exists in the URL parameters
    code = request.args.get("code")

    # Code does not exist, logging in
    if not code:
        return redirect(DISCORD_OAUTH_LINK), 302
    
    # Code exists, getting token
    else:
    
        # Make a POST request to the token API for discord
        #   Then call the Discord API to get the user's ID to store it in the permanent session
        response = post(
            DISCORD_TOKEN_LINK,
            data = {
                "client_id": environ["CLIENT_ID"],
                "client_secret": environ["CLIENT_SECRET"],
                "grant_type": "authorization_code",
                "code": code,
                "scope": "identify",
                "redirect_uri": "https://omegapsi.fellowhashbrown.com/login"
            },
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        session_data = response.json()

        response = get(
            "https://discordapp.com/api/v6/users/@me",
            headers = {
                "Authorization": "Bearer {}".format(session_data["access_token"])
            }
        )
        user_data = response.json()
        user_data.update(session_data)

        # Store the user's ID in the database and the session, proceed to /developer
        #   also keep track of when the user was verified that way
        #   the user can reauthenticate when their token expires
        user_data["verified_at"] = int(datetime.now().timestamp())
        database.data.set_session_user(user_data["id"], user_data)
        session["user_id"] = user_data["id"]
        response = make_response(
            redirect(
                f"/{session['target_url']}",
                code = 302
            )   
        )
        response.set_cookie("user_id", user_data["id"])
        return response, 302

@app.route("/developer")
def developer():

    # Check if the current session user id is a developer
    if database.bot.is_developer_sync(session.get("user_id")):

        # Get all the bug and suggestions cases and change the "author" key to
        #   show the authors name and discriminator
        bug_cases = database.case_numbers.get_bug_cases_sync()["cases"]
        for case in bug_cases:
            user = OMEGA_PSI.get_user(int(bug_cases[case]["author"]))
            bug_cases[case]["author"] = "Unknown" if not user else str(user)
            if bug_cases[case]["seen"]:
                dev = OMEGA_PSI.get_user(int(bug_cases[case]["seen"]))
                bug_cases[case]["seen"] = "Unknown" if not dev else str(dev)

        suggestion_cases = database.case_numbers.get_suggestion_cases_sync()["cases"]
        for case in suggestion_cases:
            user = OMEGA_PSI.get_user(int(suggestion_cases[case]["author"]))
            suggestion_cases[case]["author"] = "Unknown" if not user else str(user)
            if suggestion_cases[case]["seen"]:
                dev = OMEGA_PSI.get_user(int(suggestion_cases[case]["seen"]))
                suggestion_cases[case]["seen"] = "Unknown" if not dev else str(dev)
        
        # Get the pending update data
        pending_update = database.bot.get_pending_update_sync()
        if len(pending_update) == 0:
            pending_update = None
        else:
            for feature in pending_update["features"]:
                feature = pending_update["features"][feature]
                feature["datetime"] = datetime_to_string(dict_to_datetime(feature["datetime"]), short = True)
            
        # Get the file change data
        changed_files = database.bot.get_changed_files_sync()
        if len(changed_files) == 0:
            changed_files = None
        
        # Get the tasks data
        tasks = database.bot.get_tasks_sync()
        if len(tasks) == 0:
            tasks = None

        # Render the /developer page
        return render_template("developer.html",
            bug_cases = bug_cases,
            suggestion_cases = suggestion_cases,
            pending_update = pending_update,
            changed_files = changed_files,
            tasks = tasks
        )
    
    # The session user is not a developer
    return missing_access(None)

@app.route("/pendingUpdate", methods = ["POST", "PUT"])
def pending_update():

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN and session.get("user_id") and database.bot.is_developer_sync(session.get("user_id")):

        # Create a new pending update if the request is of type POST
        if request.method == "POST":

            # Create a new pending update in the database
            database.bot.create_pending_update_sync()
            return jsonify({"success": True}), 201
        
        # Commit the pending update if the request is of type PUT
        elif request.method == "PUT":

            # Commit the update in the database
            #   if the method returns False, a version with the specified version already exists
            if database.bot.commit_pending_update_sync(request.json["version"], request.json["description"]):
                return jsonify({"success": True}), 202

            # The version already exists
            return jsonify({"error": "An update with version {} already exists.".format(request.json["version"])}), 400
    
    # The origin does not match ALLOW_ORIGIN
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/pendingUpdate/feature", methods = ["POST", "PUT", "DELETE"])
def create_feature():

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN and session.get("user_id") and database.bot.is_developer_sync(session.get("user_id")):

        # Creating a feature
        if request.method == "POST":

            # Check if the pending update exists
            if len(database.bot.get_pending_update_sync()) != 0:
                feature = database.bot.add_pending_feature_sync(request.json["feature"], request.json["featureType"])
                feature["datetime"] = datetime_to_string(dict_to_datetime(feature["datetime"]), short = True)
                return jsonify(feature), 201
            
            # The pending update does not exist
            return jsonify({"error": "A pending update does not exist yet."}), 404
        
        # Updating a feature
        elif request.method == "PUT":

            # Check if the pending update exists
            if len(database.bot.get_pending_update_sync()) != 0:
                pending_update = database.bot.get_pending_update_sync()

                # Check if the feature ID exists
                if request.json["featureID"] in pending_update["features"]:
                    pending_update["features"][request.json["featureID"]].update(
                        feature = request.json["feature"],
                        type = request.json["featureType"]
                    )
                    changed_feature = pending_update["features"][request.json["featureID"]]
                    database.bot.set_pending_update_sync(pending_update)
                    return jsonify(changed_feature), 202
                
                # The feature ID does not exist
                else:
                    return jsonify({"error": "That feature does not exist!"}), 404
            
            # The pending update does not exist
            return jsonify({"error": "A pending update does not exist yet."}), 404
        
        # Removing a feature
        elif request.method == "DELETE":

            # Check if the pending update exists
            if len(database.bot.get_pending_update_sync()) != 0:

                # Check if the featureID is in the dict of features
                features = database.bot.get_pending_update_sync()["features"]
                if request.json["featureID"] in features:
                    feature = features.pop(request.json["featureID"])
                    database.bot.set_pending_update_sync({"features": features})
                    return jsonify(feature), 200
                
                # There is no feature with the specified ID
                return jsonify({"error": "Invalid feature ID ({})".format(request.json["featureID"])}), 404
        
            # There is no pending update
            return jsonify({"error": "A pending update does not exist yet."}), 404
    
    # The origin does not match ALLOW_ORIGIN
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/fileChange/file", methods = ["POST", "PUT", "DELETE"])
def file_change_file():

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN and session.get("user_id") and database.bot.is_developer_sync(session.get("user_id")):
        
        # Creating a new file
        if request.method == "POST":
            file_id = database.bot.add_file_sync(request.json["filename"])
            if file_id:
                return jsonify({"filename": request.json["filename"], "id": file_id}), 201
            return jsonify({"error": "File already exists"}), 409
        
        # Editing a file
        elif request.method == "PUT":
            file_json = database.bot.edit_file_sync(request.json["fileID"], request.json["filename"])
            if file_json:
                return jsonify(file_json), 202
            return jsonify({"error": "File does not exist"}), 404
        
        # Removing a file
        elif request.method == "DELETE":
            file_json = database.bot.remove_file_sync(request.json["fileID"])
            if file_json:
                return jsonify(file_json), 200
            return jsonify({"error": "File does not exist"}), 404
    
    # The origin does not match ALLOW_ORIGIN
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/fileChange/change", methods = ["POST", "PUT", "DELETE"])
def file_change_file_change():

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN and session.get("user_id") and database.bot.is_developer_sync(session.get("user_id")):
        
        # Creating a new change
        if request.method == "POST":
            change_id = database.bot.add_file_change_sync(request.json["fileID"], request.json["change"])
            return jsonify({"id": change_id, "change": request.json["change"]}), 201
        
        # Editing an existing change
        elif request.method == "PUT":
            change = database.bot.edit_file_change_sync(request.json["fileID"], request.json["changeID"], request.json["change"])
            if change == False:
                return jsonify({"error": "Change does not exist for file"}), 404
            elif change == None:
                return jsonify({"error": "File does not exist"}), 404
            return jsonify({"change": change}), 201
        
        # Removing a file
        elif request.method == "DELETE":
            change = database.bot.remove_file_change_sync(request.json["fileID"], request.json["changeID"])
            if change == False:
                return jsonify({"error": "Change does not exist for file"}), 404
            elif change == None:
                return jsonify({"error": "File does not exist"}), 404
            return jsonify({"change": change}), 200
    
    # The origin does not match ALLOW_ORIGIN
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/tasks", methods = ["POST", "PUT", "DELETE"])
def tasks():

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN and session.get("user_id") and database.bot.is_developer_sync(session.get("user_id")):
        
        # Adding a new task
        if request.method == "POST":
            task_json = database.bot.add_task_sync(request.json["task"])
            return jsonify(task_json), 201

        # Editing an existing task
        elif request.method == "PUT":
            task_json = database.bot.edit_task_sync(request.json["taskID"], request.json["task"])
            if task_json:
                return jsonify(task_json), 201
            return jsonify({"error": "Task does not exist"}), 404

        # Removing a task
        elif request.method == "DELETE":
            task_json = database.bot.remove_task_sync(request.json["taskID"])
            if task_json:
                return jsonify(task_json), 200
            return jsonify({"error": "Task does not exist"}), 404
    
    # The origin does not match ALLOW_ORIGIN
    return jsonify({"error": "Unauthorized"}), 401
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def run():
    app.run(host = "0.0.0.0", port = randint(1000, 9999))

def keep_alive(bot, cogs):

    # Create sections for each cog's commands
    command_sections = []
    for cog in cogs:
        if cog:
            commands = sorted(
                bot.get_cog(cog).get_commands(),
                key = lambda command: command.name
            )

            # Create section object, adding each command
            command_sections.append(Section(
                title = bot.get_cog(cog).qualified_name,
                description = bot.get_cog(cog).description,
                commands = commands
            ))

    website = Website(
        footer = Footer(
            copyright_name = "Jonah Pierce",
            copyright_year = 2018,
            links = [
                Link(url = "/privacyPolicy", text = "privacy policy"),
                Link(url = "/developer", text = "devs")
            ]
        ),
        pages = [
            Page(
                title = "commands",
                custom_title = "Omega Psi Commands",
                description = "below is a list of commands in omega psi and what they do. hover over the colored commands for more information on it.",
                sections = command_sections,
                homepage = True
            ),
            Page(
                title = "info",
                custom_title = "Info",
                description = "information about the bot goes here including the current pending update or current tasks. you can also report a bug or make a suggestion in the feedback section!",
                sections = [
                    HomeSection(
                        title = "tasks",
                        description = "the tasklist for omega psi changes, fixes, or features will be shown below!",
                        custom_html = get_tasks_html(True)
                    ),
                    HomeSection(
                        title = "pendingUpdate",
                        description = "the current pending update for Omega Psi",
                        custom_html = get_pending_update_html(False)
                    ),
                    HomeSection(
                        title = "feedback",
                        description = "if you found a bug and would like to report it or if you have a suggestion for Omega Psi",
                        custom_html = get_feedback_html()
                    )
                ]
            ),
            Page(
                title = "developer",
                custom_title = "Developer Portal",
                description = "only developers can see this ...",
                ignore = True,
                sections = [
                    HomeSection(
                        title = "bugs",
                        description = "all bug reports made by users of the bot will be displayed below",
                        custom_html = get_case_html(True)
                    ),
                    HomeSection(
                        title = "suggestions",
                        description = "all suggestions made by users of the bot will be displayed below",
                        custom_html = get_case_html(False)
                    ),
                    HomeSection(
                        title = "tasks",
                        description = "",
                        custom_html = get_tasks_html()
                    ),
                    HomeSection(
                        title = "pendingUpdate",
                        description = "all the information about a pending update goes here!",
                        custom_html = get_pending_update_html()
                    )
                ]
            ),
            Page(
                title = "settings",
                custom_title = "Settings",
                description = "use this page to manage any servers you're in (that you can manage) or your settings.",
                sections = [
                    HomeSection(
                        title = "servers",
                        description = "here's where you can change Omega Psi's settings in servers you manage",
                        custom_html = get_server_settings_html()
                    ),
                    HomeSection(
                        title = "user",
                        description = "change your own personal settings here or view your gamestats!",
                        custom_html = get_user_settings_html()
                    )
                ]
            ),
            Page(
                title = "server",
                custom_title = "Edit {{ guild.name }}",
                description = "you can edit Omega Psi's setting in {{ guild.name }} here!",
                ignore = True,
                sections = [
                    HomeSection(
                        title = "prefix",
                        description = "",
                        custom_html = get_server_settings_html(True, "prefix")
                    ),
                    HomeSection(
                        title = "disabledCommands",
                        description = "",
                        custom_html = get_server_settings_html(True, "disabledCommands")
                    )
                ]
            ),
            Page(
                title = "pageNotFound",
                custom_title = "Page Not Found",
                description = "oooof. i think you took a wrong turn :\\",
                ignore = True
            ),
            Page(
                title = "missingAccess",
                custom_title = "Missing Access",
                description = "you can't go to that page. if you think this is a mistake, please contact a developer.",
                ignore = True
            ),
            Page(
                title = "notServerManager",
                custom_title = "Not a Server Manager",
                description = "you don't have manage server permissions for that server!",
                ignore = True
            )
        ]
    )

    website.generate_html()

    thread = Thread(target = run)
    thread.start()