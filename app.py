from asyncio import run_coroutine_threadsafe
from datetime import datetime, timedelta
from discord import Embed, File
from flask import Flask, session, request, redirect, url_for, render_template, jsonify, make_response, abort
from flask_session import Session
from os import environ, remove
from random import randint
from requests import post, get
from threading import Thread

from cogs.globals import loop, PRIMARY_EMBED_COLOR
from cogs.predicates import is_developer_predicate

from util.database.database import database
from util.github import create_issue_sync, fix_issue_sync
from util.website.custom_html import get_case_html, get_pending_update_html, get_tasks_html, get_feedback_html, get_user_settings_html, get_server_settings_html, get_bot_settings_html
from util.website.page import Page, Section, HomeSection
from util.website.website import Website, Footer, Link

from util.discord import notification_handler
from util.functions import get_embed_color_sync, create_fields, add_fields
from util.string import dict_to_datetime, datetime_to_string

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

app = Flask("Omega Psi (BETA)")
app.config.update(
    SESSION_TYPE = "mongodb",
    SESSION_MONGODB = database.client,
    SESSION_MONGODB_DB = "omegapsi",
    SESSION_COOKIE_SECURE = True,
    SESSION_COOKIE_SAMESITE = 'Lax',
    SECRET_KEY = environ["SESSION_SECRET_KEY"],
    PREFERRED_URL_SCHEME = "https",
    PERMANENT_SESSION_LIFETIME = timedelta(days = 7)
)
Session(app)

DISCORD_OAUTH_LINK = "https://discord.com/api/oauth2/authorize?client_id=535587516816949248&redirect_uri=https%3A%2F%2Fomegapsi.fellowhashbrown.com%2Flogin&response_type=code&scope=identify"
DISCORD_TOKEN_LINK = "https://discord.com/api/oauth2/token"
GITHUB_ISSUE_URL = "https://github.com/FellowHashbrown/Omega-Psi/issues/{}"

OMEGA_PSI = None

ALLOW_ORIGIN = "https://omegapsi.fellowhashbrown.com"
BUG, SUGGESTION, INSULT, COMPLIMENT = 0, 1, 2, 3

notification_descriptions = {
    "update": "receive notifications when an update is made to Omega Psi",
    "new_feature": "receive notifications when a new feature is added to the current pending update in Omega Psi",
    "tasks": "receive notifications when a task is added or removed by a developer"
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.before_request
def make_session_permanent():
    """Makes the current session permanent"""
    request.environ["wsgi.url_scheme"] = "https"

    # Check if the request is made to either /developer, /info, or /settings
    #   Have the user login if needed
    if request.endpoint in ["developer", "info", "settings"]:
        session["target_url"] = request.endpoint
        session_user_id = session.get("user_id")
        cookie_user_id = request.cookies.get("user_id")
        session["user_id"] = cookie_user_id if cookie_user_id else session_user_id
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

@app.route("/", methods = ["GET", "HEAD"])
@app.route("/commands")
def commands():
    """Renders the commands webpage
    This will also control the monthly usage functionality
    """

    # If the method is HEAD, that means that UptimeRobot
    #   pinged this wepbage
    if request.method == "HEAD":

        # Retrieve the monthly usage data and check if the current timestamp
        #   is equal to or has surpassed the next update
        usage_data = database.bot.get_usage_data_sync()
        now = datetime.now()
        now_timestamp = int(now.timestamp())
        if now_timestamp >= int(usage_data["next_update"]):

            # Change the next time the stats will be sent to developers
            next_update = datetime(
                now.year + (1 if now.month != 12 else 0),
                (now.month + 1) if now.month != 12 else 1,
                1  # The first of the month will always be the day of report
            )
            
            # Create the file for all the commands and cogs
            #   That will be used for the statistics file
            f = open("{}-{}-{}-stats.txt".format(
                now.year - (1 if (now.month - 1 == 0) else 0), 
                12 if (now.month - 1 == 0) else (now.month - 1), 1
            ), "w")
            cogs = {}
            for command in OMEGA_PSI.walk_commands():
                if command.qualified_name != "help":
                    cog = command.cog.qualified_name
                    command = command.qualified_name

                    # Add the command/cog into cogs, if necessary
                    if cog not in cogs:
                        cogs[cog] = {}
                    if command not in cogs[cog]:
                        cogs[cog][command] = 0
                    
                    # Check if the command exists in the usage_data
                    if command in usage_data["commands"]:
                        cogs[cog][command] = usage_data["commands"][command]
            
            # Add the cog information to the file and the # of unique users
            file_output = f"Stats for {now.ctime()}\n"
            for cog in cogs:
                file_output += f"{cog}\n"
                for command in cogs[cog]:
                    file_output += f"\t{command}: {cogs[cog][command]}\n"
                file_output += "\n"
            
            # Write the file to the file object and send to the developer
            file_output += f"# of Unique Users: {len(usage_data['unique_users'])}\n"
            f.write(file_output)
            f.close()
            f = open(f.name, "r")
            for dev in database.bot.get_developers_sync():
                dev = OMEGA_PSI.get_user(int(dev))
                if dev:
                    developer_send = run_coroutine_threadsafe(
                        dev.send(file = File(f)),
                        loop
                    )
                    developer_send.result()
            
            # Afterwards, delete the file, it's no longer needed
            f.close()
            remove(f.name)
            
            # Now update the usage data in the database
            usage_data.update(
                cogs = {},
                commands = {},
                unique_users = [],
                next_update = str(int(next_update.timestamp()))
            )
            database.bot.set_usage_data_sync(usage_data)

    return render_template("commands.html"), 200

@app.route("/info")
def info():
    """Renders the info webpage"""

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
            feature["human_time"] = datetime_to_string(dict_to_datetime(feature["datetime"]), short = True)
            
    return render_template("info.html", 
        user_id = request.cookies.get("user_id"),
        tasks = tasks,
        pending_update = pending_update
    ), 200

@app.route("/settings")
def settings():
    """Renders the settings webpage"""

    # Get a list of guilds that Omega Psi and the user are in where the user
    #   also has manage guild permissions
    manageable_guilds = []
    for guild in OMEGA_PSI.guilds:
        member = guild.get_member(int(session.get("user_id")))
        if member and member.guild_permissions.manage_guild:
            manageable_guilds.append(guild)
    
    # Get the user data to show the update notifications, if the user is receiving them
    user_data = database.users.get_user_sync(session.get("user_id"))
    notification_data = user_data["notifications"]

    # Get the users minigame data from the database
    minigame_data = database.users.get_minigame_data_sync(session.get("user_id"))
    minigames = {}
    for data in minigame_data:
        minigame_data[data].update(
            ratio = round(
                minigame_data[data]["won"] / minigame_data[data]["lost"]
                if minigame_data[data]["lost"] > 0 else
                minigame_data[data]["won"],
                2
            )
        )
        minigames[data.replace("_", " ")] = minigame_data[data]
    
    # Get the suggestion and bug cases from the user
    bug_cases = database.case_numbers.get_bug_cases_sync(
            key = lambda case: case["author"] == session.get("user_id"))["cases"]
    suggestion_cases = database.case_numbers.get_suggestion_cases_sync(
            key = lambda case: case["author"] == session.get("user_id"))["cases"]

    return render_template("settings.html",
        manageable_guilds = manageable_guilds,
        minigames = minigames,
        notification_data = notification_data,
        notification_descriptions = notification_descriptions,
        user_color = hex(
            user_data["embed_color"]
            if user_data["embed_color"] is not None else
            PRIMARY_EMBED_COLOR
        )[2:].rjust(6, "0"),
        bug_cases = bug_cases,
        suggestion_cases = suggestion_cases
    ), 200

@app.route("/server/<string:guild_id>")
def server(guild_id):
    """Renders a server settings webpage

    :param guild_id: The guild which the webpage applies to
    """
    
    # Make sure the user can manage the guild and get the 
    #   prefix and disabled commands for the guild
    guild = OMEGA_PSI.get_guild(int(guild_id))
    if guild:
        member = guild.get_member(int(session.get("user_id")))
        if member and member.guild_permissions.manage_guild:
            return render_template("server.html",
                guild = guild,
                guild_prefix = database.guilds.get_prefix_sync(guild_id),
                disabled_commands = database.guilds.get_disabled_commands_sync(guild_id)
            )
        abort(401)
    
    # The guild can't be found or the member can't be found or the member cannot manage the guild
    abort(400)

@app.route("/favicon.ico")
def favicon():
    """Retrieves the favicon"""
    return redirect("/static/favicon.ico")

@app.route("/privacyPolicy")
def privacy_policy():
    """Renders the privacy policy webpage"""
    return render_template("privacyPolicy.html"), 200

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Errors
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.errorhandler(404)
def page_not_found(error):
    """Renders the page not found webpage"""
    return render_template("pageNotFound.html"), 404

@app.errorhandler(403)
def missing_access(error):
    """Renders the missing access webpage"""
    return render_template("missingAccess.html"), 403

@app.errorhandler(400)
def no_such_guild(error):
    """Renders the no such guild webpage"""
    return render_template("noSuchGuild.html"), 400

@app.errorhandler(401)
def not_a_guild_manager(error):
    """Renders the not a guild manager webpage"""
    return render_template("notServerManager.html"), 401

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Feedback Routes
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def create_case_embed(user, case_number, case_data, description, seen_data=None, *, case_type = 0):
    """Creates a Discord Embed to send to the user and the case channel

    :param user: The user that submitted the bug/suggestion
    :param case: The case number to give the bug/suggestion
    :param case_data: The request data which holds the source type and the source
    :param description: The description of the case
    :param seen_data: The data to determine if something has been seen by a developer
    :param case_type: The type of case to create an embed for
        0 = Bug
        1 = Suggestion
        2 = Insult
        3 = Compliment
    """
    title = ["Bug (#{})", "Suggestion (#{})", "Insult (#{})", "Compliment (#{})"][case_type]

    # Create the base embed for all case types
    #   which include bugs, suggestions, insults, and compliments
    embed = Embed(
        title = title.format(case_number),
        description = "_ _",
        colour = get_embed_color_sync(user),
        timestamp = datetime.now(),
        url = GITHUB_ISSUE_URL.format(case_data["github_issue"])
    ).add_field(
        name = "User", value = str(user)
    )

    # Bug Case Type
    if case_type == BUG:
        embed.add_field(
            name = "Source Type", value = case_data["source_type"]
        ).add_field(
            name = "Source", value = case_data["source"]
        )
    
    # Add more fields based on the type of case
    embed.add_field(
        name = ["Description", "Suggestion", "Insult", "Compliment"][case_type], 
        value = description
    ).add_field(
        name = "Seen?", value = "Yes, by {}".format(
            str(seen_data["dev"])
        ) if seen_data is not None else "No"
    ).add_field(
        name = "Fixed?" if case_type == 0 else "Considered?",
        value = "{}".format(
            "No" if case_type == 0 else "Not Yet"
        ) if not seen_data else "{}".format(
            seen_data["text"]
        )
    )

    return embed

@app.route("/reportBug", methods = ["POST", "PUT"])
def report_bug():
    """Processes the report bug API endpoint"""

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN:

        # Check if the method is POST
        if request.method == "POST":

            # Get the bug report data along with the current user and get
            #   a discord.User object from their ID
            description = request.json["description"]
            user_id = session.get("user_id")
            user = OMEGA_PSI.get_user(int(user_id))
            case_number = database.case_numbers.get_bug_number_sync()

            # Create an embed that will be sent to the developers, the bug reporter
            #   and the bug channel
            case_data = dict(request.json)
            case_data["source_type"] = case_data.pop("sourceType")
            embed = create_case_embed(
                user, case_number,
                case_data, description,
                case_type = BUG
            )
            
            channel = OMEGA_PSI.get_channel(int(environ["BUG_CHANNEL"]))
            channel_send = run_coroutine_threadsafe(channel.send(embed = embed), loop)
            msg = channel_send.result()

            # Add the bug into the database and post it onto GitHub
            issue_number = create_issue_sync(
                f"Bug #{case_number} - {str(user)}",
                (
                    "# Source Type\n {}\n" +
                    "## Source\n {}\n" +
                    "# Description\n {}\n"
                ).format(
                    case_data["source_type"],
                    case_data["source"],
                    description
                )
            )["number"]
            database.case_numbers.add_bug_sync(
                case_data["source_type"], case_data["source"],
                user, description, msg.id,
                github_issue = issue_number
            )

            # Send a message to each developer displaying what the bug is
            for dev in database.bot.get_developers_sync():
                dev = OMEGA_PSI.get_user(int(dev))
                if dev:
                    developer_send = run_coroutine_threadsafe(
                        dev.send(embed = embed),
                        loop
                    )
                    developer_send.result()
            return jsonify({"message": "Bug #{} created".format(case_number)}), 201
        
        # Check if the method is PUT; A developer has marked a bug as seen OR as fixed
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
                seen_dev = OMEGA_PSI.get_user(int(case["seen"])) if case["seen"] is not None else None

                # Update the embed with the new values and edit the original message in the bug channel
                embed = create_case_embed(
                    user, case_number,
                    case, case["bug"],
                    {
                        "dev": str(dev) if seen_dev is None else str(seen_dev),
                        "text": "Yes" if case["fixed"] else "No"
                    },
                    case_type = BUG
                )

                # Only update the message if the bug has been marked as seen or if the fixed key exists
                if case["seen"] is None or ("fixed" in request.json and not case["fixed"]):

                    # Get the message that this bug is connected to
                    channel = OMEGA_PSI.get_channel(int(environ["BUG_CHANNEL"]))
                    message = run_coroutine_threadsafe(
                        channel.fetch_message(int(case["message_id"])),
                        loop
                    )
                    message = message.result()
                    
                    # Update the message
                    update_message = run_coroutine_threadsafe(message.edit(embed = embed), loop)
                    update_message.result()

                # Check if the "fixed" key exists in the request.json
                if "fixed" in request.json:

                    # Send a message to the user saying a developer has marked their bug as fixed
                    #   only if the user was found
                    # Update the issue on GitHub
                    bug = database.case_numbers.get_bug_sync(case_number)
                    database.case_numbers.fix_bug_sync(case_number)
                    fix_issue_sync(bug["github_issue"])
                    if user and not case["fixed"]:
                        user_send = run_coroutine_threadsafe(
                            user.send(
                                embed = Embed(
                                    title = "Bug Fixed!",
                                    description = "_ _",
                                    colour = PRIMARY_EMBED_COLOR
                                ).add_field(
                                    name = "Bug (#{})".format(case_number),
                                    value = case["bug"]
                                )
                            ),
                            loop
                        )
                        user_send.result()
                    
                    # The bug was already fixed
                    elif case["fixed"]:
                        return jsonify({"bug": case_number}), 400
                    return jsonify({"message": "Bug #{} marked as fixed".format(case_number)}), 201

                else:

                    # Send a message to the user saying a developer has viewed their bug
                    #   only if the user was found and if the bug hasn't been seen already
                    database.case_numbers.mark_bug_seen_sync(case_number, dev)
                    if user and case["seen"] is None:
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
    """Processes the suggest API endpoint"""

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

            # Add the suggestion to the database and send a message to all developers
            issue_number = create_issue_sync(
                f"Suggestion #{case_number} - {str(user)}",
                "# Description\n{}".format(description),
                is_bug = False
            )["number"]

            case_data = {
                "description": description,
                "github_issue": issue_number
            }

            embed = create_case_embed(
                user, case_number,
                case_data, description,
                case_type = SUGGESTION
            )

            channel = OMEGA_PSI.get_channel(int(environ["SUGGESTION_CHANNEL"]))
            channel_send = run_coroutine_threadsafe(channel.send(embed = embed), loop)
            msg = channel_send.result()

            # Add the suggestion into the database
            database.case_numbers.add_suggestion_sync(
                user, description, 
                msg.id, github_issue = issue_number)

            # Send a message to each developer displaying what the suggestion is
            for dev in database.bot.get_developers_sync():
                dev = OMEGA_PSI.get_user(int(dev))
                if dev:
                    developer_send = run_coroutine_threadsafe(
                        dev.send(embed = embed),
                        loop
                    )
                    developer_send.result()
            return jsonify({"message": "Suggestion #{} created".format(case_number)}), 201
        
        # Check if the method is PUT; A developer has marked a suggestion as seen OR the suggestion is being considered/not considered
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
                seen_dev = OMEGA_PSI.get_user(int(case["seen"])) if case["seen"] is not None else None

                # Update the embed sent in the suggestions channel
                if "consideration" in request.json:
                    considered_text = "No\n**Reason**: {}".format(
                        request.json["consideration"]["reason"]
                    ) if not request.json["consideration"]["consider"] else "Yes"
                else:
                    if case["consideration"]:
                        considered_text = "No\n**Reason**: {}".format(
                            case["consideration"]["reason"]
                        ) if not case["consideration"]["considered"] else "Yes"
                    else:
                        considered_text = "Not Yet"
                embed = create_case_embed(
                    user, case_number,
                    case, case["suggestion"],
                    { 
                        "dev": str(dev) if seen_dev is None else str(seen_dev),
                        "text": considered_text
                    },
                    case_type = SUGGESTION
                )

                # Only update the message if the suggestion has been marked as seen or if the consideration key exists
                if case["seen"] is None or "consideration" in request.json:

                    # Get the message this suggestion is connected to
                    channel = OMEGA_PSI.get_channel(int(environ["SUGGESTION_CHANNEL"]))
                    message = run_coroutine_threadsafe(
                        channel.fetch_message(int(case["message_id"])),
                        loop
                    )
                    message = message.result()
                    
                    # Update the message
                    update_message = run_coroutine_threadsafe(message.edit(embed = embed), loop)
                    update_message.result()

                # Check if the "consideration" key exists in the request.json
                if "consideration" in request.json:
                    
                    # Send a message to the user saying their suggestion is being considered/not considered
                    #   only if the user was found
                    # Update the suggestion in GitHub
                    suggestion = database.case_numbers.get_suggestion_sync(case_number)
                    database.case_numbers.consider_suggestion_sync(
                        case_number, 
                        request.json["consideration"]["consider"],
                        request.json["consideration"]["reason"]
                    )
                    fix_issue_sync(
                        suggestion["github_issue"],
                        reason = (
                            True if request.json["consideration"]["consider"]
                            else request.json["consideration"]["reason"]))
                    if user:

                        # Set up the embed
                        embed = Embed(
                            title = "Suggestion {}Considered".format(
                                "" if request.json["consideration"]["consider"] else "Not "
                            ),
                            description = "_ _",
                            colour = PRIMARY_EMBED_COLOR
                        ).add_field(
                            name = "Suggestion (#{})".format(case_number),
                            value = case["suggestion"]
                        )

                        # Add the reason if the suggestion is not being considered
                        if not request.json["consideration"]["consider"]:
                            embed.add_field(
                                name = "Reason",
                                value = request.json["consideration"]["reason"],
                                inline = False
                            )
                        user_send = run_coroutine_threadsafe(
                            user.send(embed = embed),
                            loop
                        )
                        user_send.result()
                    return jsonify({"message": "Suggestion #{} {}considered".format(case_number, "" if request.json["consideration"]["consider"] else "not ")}), 201
            
                else:

                    # Send a message to the user saying a developer has viewed their suggestion
                    #   only if the user was found and if the suggestion hasn't been seen already
                    suggestion = database.case_numbers.get_suggestion_sync(case_number)
                    database.case_numbers.mark_suggestion_seen_sync(case_number, dev)
                    if user and case["seen"] is None:
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
                    return jsonify({"message": "Suggestion #{} marked as seen".format(case_number), "developer": str(dev)}), 201
    
    # The origin does not match ALLOW_ORIGIN
    return jsonify({"error": "Unauthorized"}), 401

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Settings Routes
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.route("/settings/user", methods = ["POST"])
def settings_user():
    """Processes the user settings API endpoint"""

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN and session.get("user_id"):

        # Changing the user's embed color
        if "embed" in request.json:
            database.users.set_embed_color_sync(session.get("user_id"), int(request.json["userColor"][1:], base = 16))
            return jsonify({"success": True}), 201
        
        # Changing the user's notifications
        elif "notification" in request.json:
            database.bot.manage_notifications_sync(
                request.json["notification"], 
                session.get("user_id"), 
                request.json["enable"])
            if request.json["notification"] == "update":
                database.users.toggle_update_notification_sync(session.get("user_id"), request.json["enable"])
            elif request.json["notification"] == "new_feature":
                database.users.toggle_new_feature_notification_sync(session.get("user_id"), request.json["enable"])
            elif request.json["notification"] == "tasks":
                database.users.toggle_tasks_notification_sync(session.get("user_id"), request.json["enable"])
            return jsonify({"success": True}), 201
    
    # The origin does not match ALLOW_ORIGIN
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/settings/server", methods = ["GET", "POST", "PUT"])
def settings_server():
    """Processes the server settings API endpoint"""

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
    """Processes login webpage/endpoint"""

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
            "https://discord.com/api/v6/users/@me",
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
    """Renders the developer webpage"""

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
        
        # Get a list of globally active commands in the bot
        all_commands = []
        all_cogs = []
        disabled_commands = database.bot.get_disabled_commands_sync()
        disabled_cogs = database.bot.get_disabled_cogs_sync()
        for command in OMEGA_PSI.walk_commands():

            # Don't add commands that have the is_developer check on it
            if (
                is_developer_predicate not in command.checks and 
                command.qualified_name not in all_commands and
                command.qualified_name not in disabled_commands and
                command.qualified_name != "help"
            ):
                all_commands.append(command.qualified_name)
        for cog in OMEGA_PSI.cogs:
            if (cog not in all_cogs and
                cog not in disabled_cogs and
                cog != "developer"):

                all_cogs.append(cog)
        
        # Get the pending update data
        pending_update = database.bot.get_pending_update_sync()
        if len(pending_update) == 0:
            pending_update = None
        else:
            for feature in pending_update["features"]:
                feature = pending_update["features"][feature]
                feature["human_time"] = datetime_to_string(dict_to_datetime(feature["datetime"]), short = True)
        
        # Get the tasks data
        tasks = database.bot.get_tasks_sync()
        if len(tasks) == 0:
            tasks = None

        # Render the /developer page
        return render_template("developer.html",
            bug_cases = bug_cases,
            suggestion_cases = suggestion_cases,
            pending_update = pending_update,
            tasks = tasks,
            disabled_commands = disabled_commands,
            disabled_cogs = disabled_cogs,
            all_commands = all_commands,
            all_cogs = all_cogs
        )
    
    # The session user is not a developer
    return missing_access(None)

@app.route("/pendingUpdate", methods = ["POST", "PUT"])
def pending_update():
    """Processes the pending update API endpoint"""

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

@app.route("/pendingUpdate/commit", methods = ["POST"])
def commit_pending_update():
    """Processes the pending update API endpoint"""

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN and session.get("user_id") and database.bot.is_developer_sync(session.get("user_id")):
        
        # Committing the update
        if request.method == "POST":
            version = request.json["version"]
            description = request.json["description"]
            user = OMEGA_PSI.get_user(int(session.get("user_id")))

            # Commit the update in the database and get the most recent
            database.bot.commit_pending_update_sync(version, description)
            update = database.bot.get_recent_update_sync()

            # Create an Embed to notify all developers
            devs = database.bot.get_developers_sync()
            for dev in devs:
                dev = OMEGA_PSI.get_user(int(dev))

                # Send to other developers except author
                if True or dev.id != user.id:
                    embed = Embed(
                        title="Update Committed by {} - (Version {})".format(
                            user, update["version"]
                        ),
                        description=update["description"],
                        colour=get_embed_color_sync(dev)
                    )
                    change_fields = create_fields(update["features"], key=lambda feature: (
                        "`{}` | {}".format(feature["type"], feature["feature"])
                    ))
                    add_fields(embed, "Changes", change_fields, empty_message="No Changes Made")
                    dev_send = run_coroutine_threadsafe(
                        dev.send(embed = embed),
                        loop)
                    dev_send.result()
            
            # Send an embed to the announcements channel
            announcements_embed = embed = Embed(
                title="New Update! Version {}".format(version),
                description=description,
                colour=PRIMARY_EMBED_COLOR)
            fields = create_fields(update["features"], key=lambda feature: (
                "`{}` | {}".format(feature["type"], feature["feature"])
            ))
            add_fields(announcements_embed, "Changes", fields, empty_message="No Changes Made")
            channel_send = run_coroutine_threadsafe(
                OMEGA_PSI.get_channel(
                    int(environ["ANNOUNCEMENTS_OMEGA_PSI"])).send(
                        "@everyone", embed=announcements_embed
                    ),
                loop)
            channel_send.result()

            # Notify users who want to be notified about the update
            commit_update_notify = run_coroutine_threadsafe(
                notification_handler(
                    OMEGA_PSI, announcements_embed,
                    "update"
                ), loop
            )
            commit_update_notify.result()

            # Send a webhook to integromat to update Facebook, Twitter, GitHub, etc.
            markdown = {
                "description": description,
                "changes": "\n".join([
                    " * `{}` | {}".format(
                        feature["type"],
                        feature["feature"]
                    )
                    for feature in update["features"]
                ])}
            regular = {
                "description": description.replace("`", ""),
                "changes": "\n".join([
                    " * |{}| - {}".format(
                        feature["type"],
                        feature["feature"].replace("`", "\'")
                    )
                    for feature in update["features"]
                ])}
            post(
                environ["INTEGROMAT_WEBHOOK_CALL"],
                json = {
                    "version": version,
                    "markdown": markdown,
                    "regular": regular
                })

            return jsonify({"success": True}), 201
    
    # The origin does not match ALLOW_ORIGIN
    return jsonify({"error": "Unauthorized"}), 401


@app.route("/pendingUpdate/feature", methods = ["POST", "PUT", "DELETE"])
def create_feature():
    """Processes the feature API endpoint"""

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN and session.get("user_id") and database.bot.is_developer_sync(session.get("user_id")):

        # Creating a feature
        if request.method == "POST":

            # Check if the pending update exists
            if len(database.bot.get_pending_update_sync()) != 0:
                feature = database.bot.add_pending_feature_sync(request.json["feature"], request.json["featureType"])
                feature["datetime"] = datetime_to_string(dict_to_datetime(feature["datetime"]), short = True)
                
                # Update all users who want to be notified of a new feature
                new_feature_notify = run_coroutine_threadsafe(
                    notification_handler(
                        OMEGA_PSI, Embed(
                            title = "Feature Added",
                            description = "\"{}\" has been added as a feature to the pending update.".format(
                                request.json["feature"]
                            )
                        ), "new_feature"
                    ), loop
                )
                new_feature_notify.result()

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

@app.route("/tasks", methods = ["POST", "PUT", "DELETE"])
def tasks():
    """Processes the tasks API endpoint"""

    # Only run if the origin is from ALLOW_ORIGIN
    if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN and session.get("user_id") and database.bot.is_developer_sync(session.get("user_id")):
        
        # Adding a new task
        if request.method == "POST":
            task_json = database.bot.add_task_sync(request.json["task"])
            user_add_task = run_coroutine_threadsafe(
                notification_handler(
                    OMEGA_PSI, Embed(
                        title = "Task Added",
                        description = "*{}* was added to the tasklist".format(request.json["task"])
                    ), "tasks"
                ), loop)
            user_add_task.result()
            
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
                user_remove_task = run_coroutine_threadsafe(
                    notification_handler(
                        OMEGA_PSI, Embed(
                            title = "Task Removed",
                            description = "*{}* was removed from the tasklist".format(task_json["task"])
                        ), "tasks"
                    ), loop)
                user_remove_task.result()
                return jsonify(task_json), 200
            return jsonify({"error": "Task does not exist"}), 404
    
    # The origin does not match ALLOW_ORIGIN
    return jsonify({"error": "Unauthorized"}), 401

@app.route("/settings/bot", methods = ["GET", "PUT"])
def settings_bot():
    """Processes the bot settings API endpoint"""

    # Getting a list of active commands
    if request.method == "GET":
        
        # Get all active commands
        all_commands = []
        all_cogs = []
        disabled_commands = database.bot.get_disabled_commands_sync()
        disabled_cogs = database.bot.get_disabled_cogs_sync()
        for command in OMEGA_PSI.walk_commands():

            # Don't add commands that have the is_developer check on it
            if (is_developer_predicate not in command.checks and 
                command.qualified_name not in all_commands and
                command.qualified_name not in disabled_commands and
                command.qualified_name != "help"):

                all_commands.append(command.qualified_name)
        for cog in OMEGA_PSI.cogs:
            if (cog not in disabled_cogs and 
                cog != "developer" and 
                cog not in all_cogs):

                all_cogs.append(cog)

        return jsonify({
            "commands": all_commands,
            "cogs": all_cogs
        }), 200

    else:

        # Only run if the origin is from ALLOW_ORIGIN
        if 'HTTP_ORIGIN' in request.environ and request.environ['HTTP_ORIGIN'] == ALLOW_ORIGIN and session.get("user_id"):

            # Enabling/Disabling a command
            if request.method == "PUT":
                if request.json["enable"]:
                    if "command" in request.json:
                        if database.bot.enable_command_sync(request.json["command"]):
                            return jsonify({"success": True}), 201
                        return jsonify({"error": "That command is already enabled!"}), 401
                    elif "cog" in request.json:
                        if database.bot.enable_cog_sync(request.json["cog"]):
                            return jsonify({"success": True}), 201
                        return jsonify({"error": "That cog is already enabled!"}), 401
                else:
                    if "command" in request.json:
                        if database.bot.disable_command_sync(request.json["command"]):
                            return jsonify({"success": True}), 201
                        return jsonify({"error": "That command is already disabled!"}), 401
                    elif "cog" in request.json:
                        if database.bot.disable_cog_sync(request.json["cog"]):
                            return jsonify({"success": True}), 201
                        return jsonify({"error": "That cog is already disabled!"}), 401
        
        # The origin does not match ALLOW_ORIGIN
        return jsonify({"error": "Unauthorized"}), 401
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def run():
    """Runs the Omega Psi website/bot"""
    app.run(host = "0.0.0.0", port = randint(1000, 9999))

def keep_alive(bot, cogs):
    """Keeps the bot alive and generates all the HTML files

    :param bot: The bot object to use
    :param cogs: The JSON of cog information
    """

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
                description = "below is a list of commands in omega psi and what they do. hover over the colored commands for more information on it. you can <a href=\"https://discord.com/oauth2/authorize?client_id=535587516816949248&scope=bot&permissions=519232\" target=\"_blank\" class=\"link\">invite omega psi</a> to your server",
                custom_description = "below is a list of commands in omega psi and what they do. hover over the colored commands for more information on it.",
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
                        title = "disabledCommands",
                        description = "",
                        custom_html = get_bot_settings_html("disabledCommands")
                    ),
                    HomeSection(
                        title = "disabledCogs",
                        description = "",
                        custom_html = get_bot_settings_html("disabledCogs")
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
                title = "noSuchGuild",
                custom_title = "No Such Guild",
                description = "Omega Psi is not in that guild",
                ignore = True
            ),
            Page(
                title = "notServerManager",
                custom_title = "Not a Server Manager",
                description = "you don't have manage server permissions for that server!",
                ignore = True
            ),
            Page(
                title = "privacyPolicy",
                custom_title = "Privacy Policy",
                description = (
                    """
                    At Fellow Hashbrown, accessible from 
                    <a href=\"https://fellowhashbrown.com\" class=\"link\" target=\"_blank\">https://fellowhashbrown.com</a>, 
                    one of our main priorities is the privacy of our visitors. 
                    This Privacy Policy document contains types of information that is collected and 
                    recorded by Fellow Hashbrown and how we use it. <br><br>

                    If you have additional questions or require more information 
                    about our Privacy Policy, do not hesitate to contact us.<br><br>

                    This Privacy Policy applies only to our online activities and 
                    is valid for visitors to our website with regards to the 
                    information that they shared and/or collect in Fellow Hashbrown. 
                    This policy is not applicable to any information collected offline 
                    or via channels other than this website.
                    """
                ),
                custom_description = "Privacy Policy for Fellow Hashbrown",
                ignore = True,
                sections = [
                    Section(
                        strict_title = True,
                        title = "consent",
                        description = "By using our website, you hereby consent to our Privacy Policy and agree to its terms."
                    ),
                    Section(
                        strict_title = True,
                        title = "information we collect",
                        description = (
                            """
                            The personal information that you are asked to provide, and the reasons why 
                            you are asked to provide it, will be made clear to you at the point we ask 
                            you to provide your personal information.

                            If you contact us directly, we may receive additional information about you 
                            such as your name, email address, phone number, the contents of the message 
                            and/or attachments you may send us, and any other information you may choose 
                            to provide.

                            When you register for an Account, we may ask for your contact information, 
                            including items such as name, company name, address, email address, 
                            and telephone number.
                            """
                        )
                    ),
                    Section(
                        strict_title = True,
                        title = "how we use your information",
                        description = (
                            """
                            We use the information we collect in various ways, including to:

                            <ul style=\"text-align: left;\">
                                <li> Provide, operate, and maintain our website </li>
                                <li> Improve, personalize, and expand our website </li>
                                <li> Understand and analyze how you use our website </li>
                                <li> Develop new products, services, features, and functionality </li>
                                <li> Communicate with you, either directly or through one of our partners, 
                                including for customer service, to provide you with updates and other 
                                information relating to the webste, and for marketing and promotional 
                                purposes </li>
                                <li> Send you emails </li>
                                <li> Find and prevent fraud </li>
                            </ul>
                            """
                        )
                    ),
                    Section(
                        strict_title = True,
                        title = "log files",
                        description = (
                            """
                            Fellow Hashbrown follows a standard procedure of using log files. 
                            These files log visitors when they visit websites. 
                            All hosting companies do this and a part of hosting services' analytics. 
                            The information collected by log files include internet protocol (IP) addresses, 
                            browser type, Internet Service Provider (ISP), date and time stamp, referring/exit pages, 
                            and possibly the number of clicks. These are not linked to any information that is personally 
                            identifiable. The purpose of the information is for analyzing trends, 
                            administering the site, tracking users' movement on the website, and 
                            gathering demographic information. <br><br>
                            
                            Our Privacy Policy was created with the help of the 
                            <a href=\"https://www.privacypolicygenerator.info/\" class=\"link\" target=\"_blank\">Privacy Policy Generator</a> and the 
                            <a href=\"https://www.privacypolicytemplate.net/\" class=\"link\" target=\"_blank\">Privacy Policy Template</a>.
                            """
                        )
                    ),
                    Section(
                        strict_title = True,
                        title = "cookies and web beacons",
                        description = (
                            """
                            Like any other website, Fellow Hashbrown uses 'cookies'. These cookies are used to store 
                            information including visitors' preferences, and the pages on the website that the 
                            visitor accessed or visited. The information is used to optimize the users' experience by 
                            customizing our web page content based on visitors' browser type and/or other information.
                            """
                        )
                    ),
                    Section(
                        strict_title = True,
                        title = "advertising partners privacy policies",
                        description = (
                            """
                            You may consult this list to find the Privacy Policy for each of the 
                            advertising partners of Fellow Hashbrown.

                            Third-party ad servers or ad networks uses technologies like cookies, 
                            JavaScript, or Web Beacons that are used in their respective advertisements 
                            and links that appear on Fellow Hashbrown, which are sent directly to users' browser. 
                            They automatically receive your IP address when this occurs. 
                            These technologies are used to measure the effectiveness of their advertising campaigns 
                            and/or to personalize the advertising content that you see on websites that you visit.

                            Note that Fellow Hashbrown has no access to or control over these cookies that are 
                            used by third-party advertisers.
                            """
                        )
                    ),
                    Section(
                        strict_title = True,
                        title = "third party privacy policies",
                        description = (
                            """
                            Fellow Hashbrown's Privacy Policy does not apply to other advertisers or websites. 
                            Thus, we are advising you to consult the respective Privacy Policies of these third-party 
                            ad servers for more detailed information. It may include their practices and instructions 
                            about how to opt-out of certain options.

                            You can choose to disable cookies through your individual browser options. 
                            To know more detailed information about cookie management with specific web browsers, 
                            it can be found at the browsers' respective websites.
                            """
                        )
                    ),
                    Section(
                        strict_title = True,
                        title = "ccpa privacy rights (do not sell my personal information)",
                        description = (
                            """
                            Under the CCPA, among other rights, California consumers have the right to:

                            <ul style=\"text-align: left;\">
                                <li> Request that a business that collects a consumer's personal data 
                                disclose the categories and specific pieces of personal data that a 
                                business has collected about consumers. </li>

                                <li> Request that a business delete any personal data about the consumer 
                                that a business has collected. </li>

                                <li> Request that a business that sells a consumer's personal data, 
                                not sell the consumer's personal data. </li>

                                <li> If you make a request, we have one month to respond to you. 
                                If you would like to exercise any of these rights, please contact us. </li>
                            </ul>
                            """
                        )
                    ),
                    Section(
                        strict_title = True,
                        title = "gdpr data protection rights",
                        description = (
                            """
                            We would like to make sure you are fully aware of all of your data protection rights. 
                            Every user is entitled to the following:

                            <ul style=\"text-align: left;\">
                                <li> The right to access – You have the right to request copies 
                                of your personal data. We may charge you a small fee for this service. </li> 

                                <li> The right to rectification – You have the right to request 
                                that we correct any information you believe is inaccurate. 
                                You also have the right to request that we complete the information you 
                                believe is incomplete. </li> 

                                <li> The right to erasure – You have the right to request that we 
                                erase your personal data, under certain conditions. </li> 

                                <li> The right to restrict processing – You have the right to request 
                                that we restrict the processing of your personal data, 
                                under certain conditions. </li> 

                                <li> The right to object to processing – You have the right to object to our 
                                processing of your personal data, under certain conditions. </li> 

                                <li> The right to data portability – You have the right to request that we 
                                transfer the data that we have collected to another organization, 
                                or directly to you, under certain conditions. </li> 
                            </ul>
                            If you make a request, we have one month to respond to you. 
                            If you would like to exercise any of these rights, please contact us.
                            """
                        )
                    ),
                    Section(
                        strict_title = True,
                        title = "children's information",
                        description = (
                            """
                            Another part of our priority is adding protection for children while using the 
                            internet. We encourage parents and guardians to observe, participate in, 
                            and/or monitor and guide their online activity.

                            Fellow Hashbrown does not knowingly collect any Personal Identifiable 
                            Information from children under the age of 13. If you think that your child 
                            provided this kind of information on our website, we strongly encourage you to 
                            contact us immediately and we will do our best efforts to promptly remove such 
                            information from our records.
                            """
                        )
                    )
                ]
            )
        ]
    )

    website.generate_html()

    thread = Thread(target = run)
    thread.start()