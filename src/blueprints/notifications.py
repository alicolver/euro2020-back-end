from database.orm import Prediction, Match
from sqlalchemy.sql import exists
from flask_mail import Mail, Message
import datetime
import pytz
from predictions import def check_kicked_off

matches = session.query(Match).filter(
        Match.match_date >= today).filter(Match.match_date <= tomorrow).all()

email_message = """
Hello {user} 

You have forgotten to put a prediction for the {game} euros game.

You stil have 1 hour to submit your prediction by visiting www.alicolver.com/euro2020

Good luck!
"""

@notifications.route('/check_for_predictions', methods=['POST'])
def check_upcoming_games()

    timezone = pytz.timezone('Europe/London')
    today = datetime.today()
    today = datetime(today.year, today.month, today.day)
    matches = session.query(Match).filter(Match.match_date = today).all()
    for match in matches:
        kick_off = getattr(match, 'kick_off_time')
        match_date = getattr(match, 'match_date')
        combined = datetime.combine(match_date, kick_off)
        combined = timezone.localize(combined)
        
        current_time = datetime.now(timezone)

        if combined < (current_time + datetime.timedelta(hours = 1)) and not check_kicked_off(match.matchid):
            check_user_prediction(match.matchid)

def check_user_prediction(match):
    users = session.query(User).filter(User.hidden == False).all()
    for user in users:
        if session.query(exists().where(Prediction.userid == userid).where(Prediction.matchid == match.matchid)).scalar():
            pass
        else:
            send_email_reminder(user, match)

def send_email_reminder(user, matchid):
    mail = Mail(app)
    email = user.email
    msg = Message("Subject", sender = "euros2020predictions@gmail.com", recipients = [email])
    msg.body = email_message.format(
        user = user.name
        game = "{} vs {}".format(match.teamone.name, match.teamtwo.name)
    )
    mail.send(msg)