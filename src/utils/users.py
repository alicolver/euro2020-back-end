import jwt
import requests
import smtplib
import ssl
from flask import jsonify
from flask_mail import Mail, Message
from utils.environment_variables import JWT_KEY, JWT_ALGORITHM
from utils.mail import mail


def get_userid(jwt_token):
    if jwt_token:
        try:
            payload = jwt.decode(jwt_token, JWT_KEY,
                                 algorithms=[JWT_ALGORITHM])

        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return jsonify({'message': 'INVALID TOKEN'})

        if 'user_id' in payload:
            return payload['user_id']
        return payload['userid']
