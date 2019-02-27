import base64, os, requests
from datetime import datetime, timedelta
from flask import Flask, render_template, session, redirect, request, flash, jsonify
from random import randint
from threading import Thread

# Load the database
from database import database

# Load email and IFTTT push functions
from util.email import send_email
from util.ifttt import ifttt_push_sync

# Load website builder
from website.website import Website
from website.page import Page, KeySection, Section
from website.page import HomeSection, Form

# Open new web app
app = Flask("Omega Psi")
app.config.update(
    SECRET_KEY = os.environ["SESSION_SECRET"],
    PERMANENT_SESSION_LIFETIME = timedelta(weeks = 1)
)

@app.route("/", methods = ["GET", "POST"])
def home():

    # Check if the method is a post method
    if request.method == "POST":
        
        # Get the form as a dict
        form = dict(request.form)
        
        # Only run if the form is not empty
        if len(form) > 0:

            # Request the users data
            response = requests.get(
                "https://discordapp.com/api/users/@me",
                headers = {
                    "Authorization": "Bearer {}".format(
                        session["__discord"]["access_token"]
                    ),
                    "Content-Type": "application/json"
                }
            )
            response = response.json()

            # Get user's email and id
            user_email = response["email"]
            user_id = response["id"]
            user_name = response["username"]
            user_discr = response["discriminator"]
            
            # Get the first thing available
            form_type = None
            form_value = None
            for key in form:
                form_type = key
                form_value = form[key][0]
                break
            
            # Check which type it is from
            subject_text = None
            plain_text = None
            html_text = None
            should_send_email = False
            flash_message = None
            if form_type == "suggest":
                if len(form_value) == 0:
                    flash("you need to enter the suggestion you want to suggest.", "error")
                else:

                    # Add the suggestion to the suggestions
                    suggestion_number = database.case_numbers.get_suggestion_number_sync()
                    database.case_numbers.add_suggestion_sync(
                        form_value,
                        user_id,
                        user_email
                    )

                    # Try to email the person
                    should_send_email = True
                    subject_text = "Suggestion Case (#{})".format(suggestion_number)
                    plain_text = "Your suggestion was sent.\n{}".format(
                        form_value
                    )
                    html_text = "<p>Your suggestion was sent.</p><br><em>{}</em>".format(
                        form_value
                    )
                    flash_message = plain_text

                    # Send a push notification
                    ifttt_push_sync(
                        subject_text,
                        "From: {}#{}\n".format(user_name, user_discr),
                        form_value
                    )
            
            elif form_type == "bug":
                if len(form_value) == 0:
                    flash("you need to enter the bug you want to report.", "error")
                else:

                    # Add the bug report to the bugs
                    bug_number = database.case_numbers.get_bug_number_sync()
                    database.case_numbers.add_bug_sync(
                        form_value,
                        user_id,
                        user_email
                    )

                    # Try to email the person
                    should_send_email = True
                    subject_text = "Bug (#{})".format(bug_number)
                    plain_text = "Your bug was reported.\n{}".format(
                        form_value
                    )
                    html_text = "<p>Your bug was reported.</p><br><em>{}</em>".format(
                        form_value
                    )
                    flash_message = plain_text

                    # Send a push notification
                    ifttt_push_sync(
                        subject_text,
                        "From: {}#{}\n".format(user_name, user_discr),
                        form_value
                    )
            
            elif form_type == "insult":
                if len(form_value) == 0:
                    flash("you need to enter the insult you want to suggest.", "error")
                else:

                    # Add the insult to the pending insults
                    database.data.add_pending_insult_sync(
                        form_value,
                        user_id,
                        user_email
                    )

                    # Try to email the person
                    should_send_email = True
                    subject_text = "Custom Insult"
                    plain_text = "Your custom insult was sent.\n{}".format(
                        form_value
                    )
                    html_text = "<p>Your custom insult was sent.</p><br><em>{}</em>".format(
                        form_value
                    )
                    flash_message = plain_text

                    # Send a push notification
                    ifttt_push_sync(
                        subject_text,
                        "From: {}#{}\n".format(user_name, user_discr),
                        form_value
                    )
            
            elif form_type == "hangman":
                if len(form_value) == 0:
                    flash("you need to enter the hangman phrase you want to suggest.", "error")
                else:

                    # Add the hangman to the pending hangmans
                    database.data.add_pending_hangman_word_sync(
                        form_value,
                        user_id,
                        user_email
                    )

                    # Try to email the person
                    should_send_email = True
                    subject_text = "Hangman Phrase"
                    plain_text = "Your hangman phrase was sent.\n{}".format(
                        form_value
                    )
                    html_text = "<p>Your hangman phrase was sent.</p><br><em>{}</em>".format(
                        form_value
                    )
                    flash_message = plain_text

                    # Send a push notification
                    ifttt_push_sync(
                        subject_text,
                        "From: {}#{}\n".format(user_name, user_discr),
                        form_value
                    )
            
            elif form_type == "scramble":
                if len(form_value) == 0:
                    flash("you need to enter the scramble phrase you want to suggest.", "error")
                else:

                    # Add the scramble to the pending scrambles
                    database.data.add_pending_scramble_word_sync(
                        form_value,
                        user_id,
                        user_email
                    )

                    # Try to email the person
                    should_send_email = True
                    subject_text = "Scramble Phrase"
                    plain_text = "Your scramble phrase was sent.\n{}".format(
                        form_value
                    )
                    html_text = "<p>Your scramble phrase was sent.</p><br><em>{}</em>".format(
                        form_value
                    )
                    flash_message = plain_text

                    # Send a push notification
                    ifttt_push_sync(
                        subject_text,
                        "From: {}#{}\n".format(user_name, user_discr),
                        form_value
                    )
            
            # Try sending the email
            if should_send_email:
                sent_email = True
                try:
                    send_email(
                        user_email,
                        subject_text,
                        plain_text,
                        html_text
                    )
                except:
                    sent_email = False
                
                # Flash an alert message just in case
                flash(
                    flash_message + "{}".format(
                        ("\n" + "You were sent an email too!") if sent_email else ""
                    ), 
                    "info"
                )
        
        # Someone tried using a post method
        else:
            return jsonify({"error": "lmao nice try. this url doesn't accept that kind of post method."}), 400
    
    # Method is a regular get method
    else:
    
        # Get code parameter from url
        code = request.args.get("code", default = None, type = str)

        # Check if __discord exists in the current session
        new_session = True
        if "__discord" in session:

            # Check if current session has not expired yet
            current = int(datetime.now().timestamp())
            if current < session["__discord"]["end"]:
                new_session = False
        
        # A new session needs to be created
        if new_session:

            # Check if code exists
            if code:

                # Get credentials for discord API request
                credentials = base64.b64encode(
                    "{}:{}".format(
                        os.environ["BOT_ID"],
                        os.environ["BOT_SECRET"]
                    ).encode()
                ).decode()

                # Request the discord API to get an access token

                response = requests.post(
                    "https://discordapp.com/api/oauth2/token",
                    data = {
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": "https://omegapsi.fellowhashbrown.com"
                    },
                    headers = {
                        "Authorization": "Basic {}".format(
                            credentials
                        )
                    }
                )
                response = response.json()

                # Set the current session as the discord user's information
                session["__discord"] = response
                session["__discord"]["end"] = int(datetime.now().timestamp()) + response["expires_in"]
            
            # Code does not exist, redirect to discord's oauth
            else:
                return redirect(
                    "https://discordapp.com/oauth2/authorize?client_id={}&scope=identify+email&response_type=code&redirect_uri=https://omegapsi.fellowhashbrown.com".format(
                        os.environ["BOT_ID"]                
                    )
                )
        
    # Everything is okay, render home.html
    return render_template("home.html")

@app.route("/commands")
def commands():
    return render_template("commands.html")

@app.errorhandler(404)
def page_not_found():
    return render_template("pageNotFound.html")

def run():
    app.run(host = "0.0.0.0", port = 5000) #randint(1000, 9999))

def keep_alive(bot = None, cogs = None):

    # Create website
    command_sections = [
        Section(title = cog, commands = sorted(bot.get_cog(cog).get_commands(), key = lambda command: command.name)) 
        for cog in cogs
    ]
    website = Website(
        pages = [
            Page(
                title = "home",
                description = "here's the website for omega psi! below, you can suggest stuff or report a bug.",
                homepage = True,
                sections = [
                    HomeSection(
                        title = "suggest",
                        description = "if you think you have a good idea (or even a great idea) for omega psi, please suggest it below!",
                        forms = [
                            Form(
                                form_name = "suggest",
                                placeholder = "enter your suggestion here",
                                button_text = "suggest",
                                target = "/"
                            )
                        ]
                    ),
                    HomeSection(
                        title = "bug",
                        description = "did you find something that resembles that of a bug? report it here! be sure to give a decent description of it so i know what to test for.",
                        forms = [
                            Form(
                                form_name = "bug",
                                placeholder = "report your bug here",
                                button_text = "report bug",
                                target = "/"
                            )
                        ]
                    ),
                    HomeSection(
                        title = "insult",
                        description = "do the insults bore you? suggest more here!",
                        forms = [
                            Form(
                                form_name = "insult",
                                placeholder = "suggest an insult here",
                                button_text = "suggest insult",
                                target = "/"
                            )
                        ]
                    ),
                    HomeSection(
                        title = "hangman",
                        description = "would you like more hangman phrases in omega psi? suggest it below",
                        forms = [
                            Form(
                                form_name = "hangman",
                                placeholder = "suggest a hangman phrase",
                                button_text = "suggest phrase",
                                target = "/"
                            )
                        ]
                    ),
                    HomeSection(
                        title = "scramble",
                        description = "do the scramble phrases not challenge you enough? suggest a more complex one here",
                        forms = [
                            Form(
                                form_name = "scramble",
                                placeholder = "suggest a scramble phrase",
                                button_text = "suggest phrase",
                                target = "/"
                            )
                        ]
                    )
                ]
            ),
            Page(
                title = "commands",
                description = "below is a list of commands in omega psi and what they do.",
                sections = [
                    KeySection()
                ] + command_sections
            ),
            Page(
                title = "website",
                description = "you shouldn't see this.",
                target = "https://www.fellowhashbrown.com"
            ),
            Page(
                title = "pageNotFound",
                description = "oooof. i think you took a wrong turn. better beep boop beep boop and go back.",
                ignore = True
            )
        ]
    )

    website.generate_html()

    thread = Thread(target = run)
    thread.start()