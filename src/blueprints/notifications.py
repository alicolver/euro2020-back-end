from blueprints.authentication import auth_required
from database.orm import Prediction, Match, User, Notification
from sqlalchemy.sql import exists
from datetime import datetime, timedelta
import pytz
from blueprints.predictions import check_kicked_off
from database.connection_manager import Session
from flask import Blueprint, jsonify, request
from typing import TYPE_CHECKING
from utils.mail import mail, sendMissingPredictionEmail
from utils.query import getUsersMissingGame
from pywebpush import webpush, WebPushException
from utils.environment_variables import EMAIL_USERNAME, PRIV_KEY
import json

session = Session()

notifications = Blueprint('notifications', __name__)


@notifications.route('/notification/subscribe', methods=['POST'])
@auth_required
def subscribe(userid):
    json_data = request.get_json()

    noti = session.query(Notification).filter(
        Notification.userid == userid).first()
    if noti is None:
        noti = Notification(
            userid=userid,
            subscription=json_data['subscription'],
        )
        session.add(noti)
    else:
        noti.subscription = json_data['subscription']

    session.commit()
    return jsonify({
        "success": True,
    })


@notifications.route('/notification/trigger', methods=['POST'])
@auth_required
def trigger(userid):
    noti = session.query(Notification).all()[0]
    data = request.get_json()
    try:
        response = webpush(
            subscription_info=json.loads(noti.subscription),
            data=data['message'],
            vapid_private_key=PRIV_KEY,
            vapid_claims={
                "sub": "mailto:{}".format(EMAIL_USERNAME)
            }
        )
        return jsonify({
            "success": True,
        })
    except WebPushException as ex:
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                  extra.code,
                  extra.errno,
                  extra.message
                  )
        return jsonify({
            "success": False,
        }), 400


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
