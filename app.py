import flask, os

from flask import Flask, render_template, redirect, request, abort, jsonify
from random import randint
from threading import Thread

from database.database import database

from util.string import get_user_info_html

# Load website builder
from website.website import Website
from website.page import Page, KeySection, Section
from website.page import UserInfoForm, HomeSection

# Open new web app
app = Flask("Omega Psi")

OMEGA_PSI_BOT = None

# # # # # # # # # # # # # # # # # # # # # # # # #
# Routes
# # # # # # # # # # # # # # # # # # # # # # # # #

@app.route("/")
def commands():
    return render_template("commands.html")

@app.route("/commands")
def commands2():
    return redirect("/")

@app.route("/user", methods = ["POST", "GET"])
def user():

    # Check if doing regular get request, return the webpage
    if request.method == "GET":
        return render_template("user.html")
    
    # Check if doing a post request, redirect to the userInfo url
    elif request.method == "POST":
        
        # Get the form values
        user_name = request.form["user_name"]
        user_discriminator = request.form["user_discriminator"]

        # Redirect the webpage
        return redirect("https://omegapsi.fellowhashbrown.com/user/{}/{}".format(user_name, user_discriminator))

@app.route("/user/<string:username>/<string:discriminator>")
def user_info(username, discriminator):
    
    # Check that the target exists
    users = OMEGA_PSI_BOT.get_all_members()
    target = None
    for user in users:
        if user.name.lower() == username.lower() and user.discriminator == discriminator:
            target = user
            break
    
    # Target exists, load the data
    if target != None:

        # Load the gamestats from the database
        target_data = database.users.get_user_sync(target)

        hangman = target_data["hangman"]
        if hangman["lost"] == 0:
            hangman["ratio"] = hangman["won"]
        else:
            hangman["ratio"] = round(hangman["won"] / hangman["lost"], 2)

        scramble = target_data["scramble"]
        if scramble["lost"] == 0:
            scramble["ratio"] = scramble["won"]
        else:
            scramble["ratio"] = round(scramble["won"] / scramble["lost"], 2)
        
        rps = target_data["rps"]
        if rps["lost"] == 0:
            rps["ratio"] = rps["won"]
        else:
            rps["ratio"] = round(rps["won"] / rps["lost"], 2)
        
        tic_tac_toe = target_data["tic_tac_toe"]
        if tic_tac_toe["lost"] == 0:
            tic_tac_toe["ratio"] = tic_tac_toe["won"]
        else:
            tic_tac_toe["ratio"] = round(tic_tac_toe["won"] / tic_tac_toe["lost"], 2)
        
        connect_four = target_data["connect_four"]
        if connect_four["lost"] == 0:
            connect_four["ratio"] = connect_four["won"]
        else:
            connect_four["ratio"] = round(connect_four["won"] / connect_four["lost"], 2)
        
        cards_against_humanity = target_data["cards_against_humanity"]
        if cards_against_humanity["lost"] == 0:
            cards_against_humanity["ratio"] = cards_against_humanity["won"]
        else:
            cards_against_humanity["ratio"] = round(cards_against_humanity["won"] / cards_against_humanity["lost"], 2)
        
        uno = target_data["uno"]
        if uno["lost"] == 0:
            uno["ratio"] = uno["won"]
        else:
            uno["ratio"] = round(uno["won"] / uno["lost"], 2)
        
        game_of_life = target_data["game_of_life"]
        if game_of_life["lost"] == 0:
            game_of_life["ratio"] = game_of_life["won"]
        else:
            game_of_life["ratio"] = round(game_of_life["won"] / game_of_life["lost"], 2)
        
        trivia = target_data["trivia"]
        if trivia["lost"] == 0:
            trivia["ratio"] = trivia["won"]
        else:
            trivia["ratio"] = round(trivia["won"] / trivia["lost"], 2)
        
        # Render the webpage for the user info
        return render_template(
            "userInfo.html",
            username = target.name,
            discriminator = target.discriminator,
            usericon = target.avatar_url_as(format="png"),
            hangman = hangman,
            scramble = scramble,
            rps = rps,
            tic_tac_toe = tic_tac_toe,
            connect_four = connect_four,
            cards_against_humanity = cards_against_humanity,
            uno = uno,
            game_of_life = game_of_life,
            trivia = trivia
        )
    
    # Target does not exist
    return abort(400)

# # # # # # # # # # # # # # # # # # # # # # # # #
# Errors
# # # # # # # # # # # # # # # # # # # # # # # # #

@app.errorhandler(404)
def page_not_found(error):
    return render_template("pageNotFound.html"), 404

@app.errorhandler(400)
def user_not_found(error):
    return render_template("userNotFound.html"), 400

# # # # # # # # # # # # # # # # # # # # # # # # #
# IFTTT API Routes
# # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # #
# Flask Setup
# # # # # # # # # # # # # # # # # # # # # # # # #

def run():
    app.run(host = "0.0.0.0", port = randint(1000, 9999))

def keep_alive(bot = None, cogs = None):

    # Create website
    command_sections = []
    for cog in cogs:

        # Create title for cog section
        title = cog.title()
        if "caps" in cogs[cog]:
            if cogs[cog]["caps"]:
                title = cog.upper()
        
        # Get sorted list of commands in cog
        commands = sorted(bot.get_cog(cog).get_commands(), key = lambda command: command.name)

        # Create section object and add to list
        command_sections.append(Section(
            title = title,
            description = cogs[cog]["description"],
            commands = commands
        ))

    # Create website object
    website = Website(
        pages = [
            Page(
                title = "commands",
                description = "below is a list of commands in omega psi and what they do.",
                sections = [
                    KeySection()
                ] + command_sections
            ),
            Page(
                title = "user",
                description = "you can use this page to look up stats and info about a user in discord as long as they are in a server with omega psi.",
                sections = [
                    HomeSection(
                        title = "enterInfo",
                        description = "use this form to enter in the username and discriminator of the discord user you wanna look up.",
                        forms = [
                            UserInfoForm(
                                form_user_name = "user_name",
                                form_user_discriminator = "user_discriminator",
                                button_text = "search user",
                                target = "/user"
                            )
                        ]
                    )
                ]
            ),
            Page(
                title = "userInfo",
                description = "below is info about the discord user <br><span class=\"code-string\">{{ username }}#{{ discriminator }}</span>",
                custom_icon = "{{ usericon }}",
                custom_title = "{{ username }}#{{ discriminator }}",
                custom_description = "below is info about the discord user {{ username }}#{{ discriminator }}",
                custom_html = get_user_info_html(),
                ignore = True
            ),
            Page(
                title = "website",
                description = "you shouldn't see this.",
                target = "https://www.fellowhashbrown.com"
            ),
            Page(
                title = "pageNotFound",
                description = "oooof. i think you took a wrong turn :\/",
                ignore = True
            ),
            Page(
                title = "userNotFound",
                description = "unfortunately, i can't find that user :(",
                ignore = True
            )
        ]
    )

    website.generate_html()

    thread = Thread(target = run)
    thread.start()