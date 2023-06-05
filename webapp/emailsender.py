import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

class EmailSender:
    def __init__(self):
        self.config = ""
        # Read and eval config file
        with open("../data/config.json", "r") as f:
            self.config = json.loads(f.read())
        self.email = self.config["SMTP_USER"]
        self.host = self.config["SMTP_HOST"]
        self.password = self.config["SMTP_PASS"]
        try: 
            self.port = int(self.config["SMTP_PORT"])
        except:
            print("Error: SMTP_PORT must be an integer")
            self.port = 587
    def send_email(self, to_email, subject, message):
        try:
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.email, self.password)
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            server.sendmail(self.email, to_email, msg.as_string())
            server.quit()
            
        except Exception as e:
            print("Error: ", e)
    
    def confirm_email(self, to_email, link):
        subject = "Email Confirmation"
        message = "Dear User,\n\nThank you for creating an account with us. Please click on the link below to confirm your email address:\n\n"+ link + "\n\nBest regards,\nThe StudSec Team"
        
        self.send_email(to_email, subject, message)
    
    def forgot_password(self, to_email, link):
        subject = "Password Reset"
        message = "Dear User,\n\nPlease click on the link below to reset your password:\n\n"+link+"\n\nBest regards,\nThe StudSec Team"
        
        self.send_email(to_email, subject, message)