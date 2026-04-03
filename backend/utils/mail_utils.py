from flask_mail import Message

from app import mail


def send_email(to, subject, body, html=False):
    if not to:
        return False

    try:
        message = Message(subject=subject, recipients=[to])
        if html:
            message.html = body
        else:
            message.body = body

        mail.send(message)
        return True
    except Exception:
        return False
