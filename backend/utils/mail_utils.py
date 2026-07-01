from flask_mail import Message


def send_email(to, subject, body, html=False):
    if not to:
        return False

    try:
        from app import mail

        message = Message(subject=subject, recipients=[to])
        if html:
            message.html = body
        else:
            message.body = body

        mail.send(message)
        return True
    except Exception as error:
        print(f"Email send failed for {to}: {error}")
        return False
