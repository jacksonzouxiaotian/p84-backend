# research_assistant/utils/email_utils.py
from flask_mail import Message
from research_assistant.extensions import mail
from flask import current_app

def send_email(subject, recipients, body):
    try:
        msg = Message(subject=subject, recipients=recipients, body=body)
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {e}")
        return False
