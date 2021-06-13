import jwt
import requests
import smtplib
import ssl
from flask import jsonify
from flask_mail import Mail, Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.environment_variables import JWT_KEY, JWT_ALGORITHM
from utils.mail_init import mail_object


def get_userid(jwt_token):
    if jwt_token:
        try:
            payload = jwt.decode(jwt_token, JWT_KEY,
                                 algorithms=[JWT_ALGORITHM])

        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return jsonify({'message': 'INVALID TOKEN'})

        return payload['user_id']


 def reset_password_email(otp, receiver_email, name):
    msg = Message("Subject", sender = "euros2020predictions@gmail.com", recipients = [receiver_email])
    
    msg.body = ("""
     <html>
         <head>
         <h1>Your EURO 2020 Password Reset Code</h1>
         </head>
         <body>
         <p>Hi, %s<br>
            Your one time password reset code is %s.<br>
            Please return to https://alicolver.com/euro2020/reset. to reset your password.<br>
            <br>
            <br>

            EURO 2020.
         </body>
     </html>
     """ % (name, otp))

    mail_object.send(msg)
