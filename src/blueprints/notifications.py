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
from utils.query import getUsersMissingGame

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

    sub = session.query(Prediction.userid).join(Match).filter(
        Match.match_datetime > now).filter(Match.match_datetime < hour).subquery()

    rows = getUsersMissingGame(session).all()

    for row in rows:
        user = row[3]
        msg = Message("Mising Prediction",
                      sender="euros2020predictions@gmail.com", recipients=[user.email])
        msg.body = email_message.format(
            user=user.name,
            game="{} vs {}".format(row[1].name, row[2].name)
        )
        mail_object.send(msg)
    return jsonify({"message": str(len(rows)) + " email(s) sent"})
