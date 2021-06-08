import jwt
import requests
import smtplib
import ssl
from flask import jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.environment_variables import JWT_KEY, JWT_ALGORITHM, EMAIL_PASSWORD


def get_userid(jwt_token):
    if jwt_token:
        try:
            payload = jwt.decode(jwt_token, JWT_KEY,
                                 algorithms=[JWT_ALGORITHM])

        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return jsonify({'message': 'INVALID TOKEN'})

        return payload['user_id']


def reset_password_email(otp, receiver_email, name):
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "page.no.reply@gmail.com"

    message = MIMEMultipart("alternative")

    message["Subject"] = "Password Reset Code"
    message["From"] = sender_email
    message["To"] = receiver_email

    html = ("""
    <html>
        <head>
        <h1>Your Page. Password Reset Code</h1>
        </head>
        <body>
        <p>Hi, %s<br>
           Your one time password reset code is %s.<br>
           Please return to Page. to reset your password.<br>
           <br>
           <br>

           Page.
        </body>
    </html>
    """ % (name, otp))

    main_message = MIMEText(html, "html")
    message.attach(main_message)

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, EMAIL_PASSWORD)
        server.sendmail(sender_email, receiver_email, message.as_string())
        return True

    return False
