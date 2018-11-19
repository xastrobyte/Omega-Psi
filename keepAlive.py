from category.help import Help

from flask import Flask, render_template
from threading import Thread

# Open new web app
app = Flask("Omega Psi")

@app.route("/")
def home():
    return render_template("index.html")

def run():
    app.run(host = "0.0.0.0", port = 1098)

def keepAlive():
    # Setup Color and Table Border Styles
    styles = (
        "   <style>\n" +
        "       body {\n" +
        "           background-color: #202020;\n" +
        "           color: #EEEEEE;\n" +
        "       }\n" +
        "       table {\n" +
        "           border-style: hidden;\n" +
        "       }\n" +
        "   </style>\n"
    )

    favicon = (
        "   <link rel=\"shortcut icon\" href=\"{{ url_for('static', filename=\"/favicon.ico\") }}\">\n" +
        "   <link rel=\"apple-touch-icon\" sizes=\"180x180\" href=\"{{ url_for('static', filename=\"/apple-touch-icon.png\") }}\">\n" +
        "   <link rel=\"icon\" type=\"image/png\" sizes=\"32x32\" href=\"{{ url_for('static', filename=\"/favicon-32x32.png\") }}\">\n" +
        "   <link rel=\"icon\" type=\"image/png\" sizes=\"16x16\" href=\"{{ url_for('static', filename=\"/favicon-16x16.png\") }}\">\n" +
        "   <link rel=\"manifest\" href=\"{{ url_for('static', filename=\"/site.webmanifest\") }}\">\n" +
        "   <link rel=\"mask-icon\" href=\"{{ url_for('static', filename=\"/safari-pinned-tab.svg\") }}\" color=\"#202020\">\n" +
        "   <meta name=\"msapplication-TileColor\" content=\"#202020\">\n" +
        "   <meta name=\"msapplication-TileImage\" content=\"{{ url_for('static', filename=\"/mstile-144x144.png\") }}\">\n" +
        "   <meta name=\"theme-color\" content=\"#202020\">\n" +
        "   <meta name=\"msapplication-config\" content=\"{{ url_for('static', filename=\"/browserconfig.xml\") }}\">\n"
    )

    html = (
        "<head>\n" +
        styles + 
        favicon +
        "</head>\n" +
        Help(None).getAllHTML()
    )

    # Generate HTML file
    htmlFile = open("templates/index.html", "w")
    htmlFile.write(html)
    htmlFile.close()

    thread = Thread(target = run)
    thread.start()
