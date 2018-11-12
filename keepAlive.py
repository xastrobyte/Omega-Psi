from category.help import Help

from flask import Flask
from threading import Thread

# Open new web app
app = Flask("Omega Psi")

@app.route("/")
def home():

    # Setup Color and Table Border Styles
    styles = (
        "<style>\n" +
        "   body {\n" +
        "       background-color: #202020;\n" +
        "       color: #EEEEEE;\n" +
        "   }\n" +
        "   table {\n" +
        "       border-style: hidden;\n" +
        "   }\n" +
        "   #primaryBorder {\n" +
        "       border: 2px solid #ce7500;\n" +
        "       padding: 10px;\n" +
        "       border-radius: 30px;\n" +
        "   }\n" +
        "   #categoryBorder {\n" +
        "       border: 2px solid #850000;\n" +
        "       padding: 10px;\n" +
        "       border-radius: 30px;\n" +
        "   }\n" +
        "   #commandBorder {\n" +
        "       border: 2px solid #005fa8;\n" +
        "       padding: 10px;\n" +
        "       border-radius: 25px;\n" +
        "   }\n" +
        "   #acceptedBorder {\n" +
        "       border: 2px solid #300000;\n" +
        "       padding: 10px;\n" +
        "       border-radius: 15px;\n" +
        "   }\n" +
        "   #noBorder {\n" +
        "       border: 0px;\n" +
        "   }\n" +
        "</style>\n"
    )

    # Setup HTML Text
    html = (
        "<!DOCTYPE html>\n" +
        "<html>\n" +
        styles +
        "   <h1><em><strong>Omega Psi</em></strong></h1>\n"+
        "   <p>A Discord Bot with commands that may just be useful and commands that are just plain fun.</p>\n" +
        "   <p>Credits:</p>\n" +
        "   <p style=\"padding-left: 30px;\">Giphy - For the gif API</p>\n" +
        "   <p style=\"padding-left: 30px;\">Sympy - For the math commands</p>\n"
    )

    # Add Top Table
    html += (
        "<table style=\"height: 48px;\" border=\"1\" width=\"773\">\n" +
        "   <tbody>\n" +
        "       <tr>\n" +
        "           <td id=\"primaryBorder\" style=\"width: 186px; text-align: center;\">\n" +
        "               <h3><strong>Commands</strong></h3>\n" +
        "               <p>Alternative Names are labeled as well</p>\n" +
        "           </td>\n" +
        "           <td id=\"primaryBorder\" style=\"width: 186px; text-align: center;\">\n" +
        "               <h3><strong>Parameters</strong></h3>\n" +
        "               [...] denotes an optional parameter\n" +
        "               <p>&lt;...&gt; denotes a required parameter</p>\n" +
        "               <h4>&nbsp;</h4>\n" +
        "           </td>\n" +
        "           <td id=\"primaryBorder\" style=\"width: 186px; text-align: center;\">\n" +
        "               <h3><strong>Action</strong></h3>\n" +
        "               <p>What the command does</p>\n" +
        "           </td>\n" +
        "           <td id=\"primaryBorder\" style=\"width: 186px; text-align: center;\">\n" +
        "               <h3><strong>Access</strong></h3>\n" +
        "               <p>Who can access the command</p>\n" +
        "           </td>\n" +
        "           <td id=\"primaryBorder\" style=\"width: 186px; text-align: center;\">\n" +
        "               <h3><strong>Private Channel</strong></h3>\n" +
        "               <p>Whether it can be run in a private channel</p>\n" +
        "           </td>\n" +
        "       </tr>\n"
    )

    html += Help(None).getAllHTML()

    return (
                    html + 
        "       </tbody>\n" +
        "   </table>\n"
        "</html>\n"
    )

def run():
    app.run(host = "0.0.0.0", port = 5000)

def keepAlive():
    thread = Thread(target = run)
    thread.start()
