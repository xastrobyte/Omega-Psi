import os, requests, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Get email and password for secure login later on
email = os.environ["USER_EMAIL"]
password = os.environ["USER_PASSWORD"]

def send_email(receiver, subject, plain_text, html_text):

    # Make sure email can be sent to
    response = requests.get("https://api.trumail.io/v2/lookups/json?email={}".format(
        receiver
    )).json()

    if not response["deliverable"]:
        raise ValueError("Cannot be delivered too.")

    # Create multipart MIME
    message = MIMEMultipart("alternative")
    message["To"] = receiver
    message["From"] = email
    message["Subject"] = subject

    # Turn plain text and html text into MIME
    plain_text = MIMEText(plain_text, "plain")
    html_text = MIMEText(html_text, "html")

    # Add both parts to multipart message
    message.attach(plain_text)
    message.attach(html_text)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context = context) as server:
        server.login(email, password)
        server.sendmail(
            email, receiver, message.as_string()
        )