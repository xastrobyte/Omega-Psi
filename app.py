from flask import Flask, render_template
from random import randint
from threading import Thread

# Open new web app
app = Flask("Omega Psi")

@app.route("/")
def home():
    return render_template("index.html")

def run():
    app.run(host = "0.0.0.0", port = 5000) #randint(1000, 9999))

def keep_alive(bot = None, cogs = None):
    # Setup Color and Table Border Styles
    styles = (
        """
            <style>
                @import url('https://fonts.googleapis.com/css?family=Cutive+Mono|Bungee+Shade|Carter+One');
                body {
                    background-color: #202020;
                    color: #EEEEEE;
                }
                table {
                    border-style: hidden;
                }
                a {
                    color: #BBBBBB;
                }

                .commands-page {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                }

                .categories-column {
                    display: flex;
                    flex-direction: column;
                }

                .category-block {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    max-width: 500px;
                    margin: 12.5px;
                }

                .category-name {
                    font-family: "Bungee Shade";
                }

                .category-info {
                    font-family: "Carter One", cursive;
                }

                .category-restriction {
                    font-family: "Carter One", cursive;
                    color: red;
                }

                .command-table {
                    border: 1px solid white;
                    border-radius: 5px;
                    padding: 5px;
                    font-family: "Thasadith"
                }

                .command-tr td {
                    padding: 5px;
                }

                .command-tags {
                    font-family: 'Cutive Mono', monospace;
                    color: #EC7600;
                }

                /* Dropdown Button */
                .dropbtn {
                    font-family: 'Bungee Inline', cursive;
                    background-color: #293134;
                    color: white;
                    font-size: 16px;
                    border: none;
                    width: 100%;
                }

                /* The container <div> - needed to position the dropdown content */
                .dropdown {
                    position: relative;
                    display: inline-block;
                    margin-left: 15%;
                    margin-right: 15%;
                    margin-bottom: 10px;
                    width: 70%;
                }

                /* Dropdown Content (Hidden by Default) */
                .dropdown-content {
                    display: none;
                    position: absolute;
                    background-color: #293134;
                    min-width: 160px;
                    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
                    z-index: 1;
                    width: 100%;
                }

                /* Links inside the dropdown */
                .dropdown-content a {
                    color: white;
                    padding: 12px 16px;
                    text-decoration: none;
                    display: block;
                }

                /* Change color of dropdown links on hover */
                .dropdown-content a:hover {
                    background-color: #121212;
                }

                /* Show the dropdown menu on hover */
                .dropdown:hover .dropdown-content {
                    display: block;
                }

                /* Change the background color of the dropdown button when the dropdown content is shown */
                .dropdown:hover .dropbtn {
                    background-color: #121212;
                }
            </style>
        """
    )

    favicon = (
        """
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        
        <link rel=\"shortcut icon\" href=\"{{ url_for('static', filename=\"/favicon.ico\") }}\">
        <link rel=\"apple-touch-icon\" sizes=\"180x180\" href=\"{{ url_for('static', filename=\"/apple-touch-icon.png\") }}\">
        <link rel=\"icon\" type=\"image/png\" sizes=\"32x32\" href=\"{{ url_for('static', filename=\"/favicon-32x32.png\") }}\">
        <link rel=\"icon\" type=\"image/png\" sizes=\"16x16\" href=\"{{ url_for('static', filename=\"/favicon-16x16.png\") }}\">
        <link rel=\"manifest\" href=\"{{ url_for('static', filename=\"/site.webmanifest\") }}\">
        <link rel=\"mask-icon\" href=\"{{ url_for('static', filename=\"/safari-pinned-tab.svg\") }}\" color=\"#202020\">
        <meta name=\"msapplication-TileColor\" content=\"#202020\">
        <meta name=\"msapplication-TileImage\" content=\"{{ url_for('static', filename=\"/mstile-144x144.png\") }}\">
        <meta name=\"theme-color\" content=\"#202020\">
        <meta name=\"msapplication-config\" content=\"{{ url_for('static', filename=\"/browserconfig.xml\") }}\">

        <meta property="theme-color" content="#EC7600" />
        <meta property="og:title" content="website.omegaPsi();" />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://www.fellowhashbrown.com/projects#omegaPsi" />
        <meta property="og:image" content="{{url_for('static', filename="/android-chrome-512x512.png")}}" />

        <meta property="og:description" content="Omega Psi Commands" />
        <meta property="og:site_name" content="Omega Psi" />
        """
    )

    # Generate bot's HTML
    commands_html = ""
    for cog in cogs:
        commands_html += get_column_html(bot, cog) + "\n"

    html = (
        "<head>\n" +
        styles + 
        favicon +
        "</head>\n" +
        "<div class=\"commands-page\">\n" +
        commands_html +
        "</div>\n"
    )

    # Generate HTML file
    htmlFile = open("templates/index.html", "w")
    htmlFile.write(html)
    htmlFile.close()

    thread = Thread(target = run)
    thread.start()

def get_column_html(bot, cog_name):

    # Setup HTML text
    html = (
        "            <div class=\"category-block\">\n" +
        "              <h2 class=\"category-name\">{}</h2>\n"
    ).format(
        cog_name
    )

    # Iterate through commands
    html += "                <table class=\"command-table\">\n"
    for command in sorted(bot.get_cog_commands(cog_name), key = lambda k: k.name):
        html += (
            "                <tr class=\"command-tr\">\n" +
            "                  <td><code>{}</code></td>\n" +
            "                  <td>{}</td>\n" +
            "                </tr>\n"
        ).format(
            command.name,
            command.description
        )
    html += "                </table>\n"

    # Add closing div tag for category block
    html += "            </div><br>\n"

    return html