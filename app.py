from flask import Flask, render_template, redirect
from threading import Thread

# Load website builder
from website.website import Website
from website.page import Page, KeySection, Section

# Open new web app
app = Flask("Omega Psi")

@app.route("/")
def commands():
    return render_template("commands.html")

@app.route("/commands")
def commands2():
    return redirect("/")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("pageNotFound.html")

def run():
    app.run(host = "0.0.0.0", port = 5000) #randint(1000, 9999))

def keep_alive(bot = None, cogs = None):

    # Create website
    command_sections = [
        Section(title = cog, description = cogs[cog]["description"], commands = sorted(bot.get_cog(cog).get_commands(), key = lambda command: command.name)) 
        for cog in cogs
    ]
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