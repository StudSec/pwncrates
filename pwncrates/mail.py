from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pwncrates import app
import smtplib
import logging


try:
    int(app.config['mailer']["SMTP_PORT"])
except ValueError:
    logging.error("SMTP port must be integer")


def send_email(to_email, subject, message):
    try:
        server = smtplib.SMTP(app.config['mailer']["SMTP_HOST"], app.config['mailer']["SMTP_PORT"])
        server.starttls()
        server.login(app.config['mailer']["SMTP_USER"], app.config['mailer']["SMTP_PASS"])
        msg = MIMEMultipart()
        msg['From'] = app.config['mailer']["SMTP_USER"]
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        server.sendmail(app.config['mailer']["SMTP_USER"], to_email, msg.as_string())
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
