from database.orm import Prediction, Match, User
from sqlalchemy.sql import exists
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import pytz
from blueprints.predictions import check_kicked_off
from database.connection_manager import Session
from flask import Blueprint, jsonify
from typing import TYPE_CHECKING
from utils.mail_init import mail_object

session = Session()

notifications = Blueprint('notifications', __name__)

email_message = """
Hello {user} 

You have forgotten to put a prediction for the {game} euros game.

You stil have 1 hour to submit your prediction by visiting www.alicolver.com/euro2020

Good luck!
"""


@notifications.route('/check_for_predictions', methods=['GET'])
def check_upcoming_games():

    timezone = pytz.timezone('Europe/London')
    now = datetime.now(timezone)
    hour = now + timedelta(hours=1)

    matches = session.query(Match).filter(
        Match.match_datetime > now).filter(Match.match_datetime < hour).all()

    for match in matches:
        check_user_prediction(match)
    return jsonify({"message": "no games in the next hour"})


def check_user_prediction(match):
    users = session.query(User).filter(User.hidden == False).all()
    for user in users:
        if not session.query(exists().where(Prediction.userid == user.userid).where(Prediction.matchid == match.matchid)).scalar():
            send_email_reminder(user, match)
    return jsonify({"message": "Reminder emails sent"})


def send_email_reminder(user, match):
    email = user.email
    msg = Message("Mising Prediction",
                  sender="euros2020predictions@gmail.com", recipients=[email])
    msg.body = email_message.format(
        user=user.name,
        game="{} vs {}".format(match.team_one.name, match.team_two.name)
    )
    mail_object.send(msg)
