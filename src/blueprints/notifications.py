from database.orm import Prediction, Match, User
from sqlalchemy.sql import exists
from datetime import datetime, timedelta
import pytz
from blueprints.predictions import check_kicked_off
from database.connection_manager import Session
from flask import Blueprint, jsonify
from typing import TYPE_CHECKING
from utils.mail import mail, sendMissingPredictionEmail
from utils.query import getUsersMissingGame

session = Session()

notifications = Blueprint('notifications', __name__)


@notifications.route('/check_for_predictions', methods=['GET'])
def check_upcoming_games():

    timezone = pytz.timezone('Europe/London')
    now = datetime.now(timezone)
    hour = now + timedelta(hours=1)

    sub = session.query(Prediction.userid).join(Match).filter(
        Match.match_datetime > now).filter(Match.match_datetime < hour).subquery()

    rows = getUsersMissingGame(session).all()

    for row in rows:
        sendMissingPredictionEmail(
            row[3].name, row[3].email, row[1].name, row[2].name)
    return jsonify({"message": str(len(rows)) + " email(s) sent"})
