from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from webapp import app
import smtplib
import json


# Read and eval config file
with open("config.json", "r") as f:
    config = json.loads(f.read())

try:
    int(config["SMTP_PORT"])
except ValueError:
    logging.error("SMTP port must be integer")


def send_email(to_email, subject, message):
    try:
        server = smtplib.SMTP(config["SMTP_HOST"], config["SMTP_PORT"])
        server.starttls()
        server.login(config["SMTP_USER"], config["SMTP_PASS"])
        msg = MIMEMultipart()
        msg['From'] = config["SMTP_USER"]
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        server.sendmail(config["SMTP_USER"], to_email, msg.as_string())
        server.quit()

    except Exception as e:
        app.logger.error("Error sending email: ")
        app.logger.error(e, exc_info=True)
        return "Failed to send email"

    return None


def confirm_email(to_email, link):
    subject = "Email Confirmation"
    message = f"""Dear User,

Thank you for creating an account with us. Please click on the link below to confirm your email address:

{link}

Best regards,
The StudSec Team
"""

    return send_email(to_email, subject, message)


def forgot_password(to_email, link):
    subject = "Password Reset"
    message = f"""Dear User,

Please click on the link below to reset your password:

{link}

Best regards,
The StudSec Team
"""

    return send_email(to_email, subject, message)
