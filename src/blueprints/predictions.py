from flask import Blueprint, jsonify, request, redirect
from sqlalchemy.sql import exists
from sqlalchemy import inspect
from database.connection_manager import Session
from blueprints.authentication import auth_required
from database.orm import Prediction, Match, Team
from sqlalchemy.exc import SQLAlchemyError
import pytz
from datetime import datetime, timedelta, time

session = Session()


predictions = Blueprint('predictions', __name__)


def check_kicked_off(matchid):
    match = session.query(Match).filter(
        Match.matchid == matchid)[0]

    timezone = pytz.timezone('Europe/London')

    current_time = datetime.now(timezone)

    return match.match_datetime < current_time


@predictions.route('/prediction', methods=['POST'])
@auth_required
def createPrediction(userid):

    data = request.get_json()

    already = session.query(exists().where(
        Prediction.userid == userid).where(Prediction.matchid == data['matchid'])).scalar()

    if already:
        update_prediction(userid, data)
        return jsonify({
            'success': True,
            'message': 'Prediction updated'
        })

    if check_kicked_off(data['matchid']):
        return jsonify({
            'success': False,
            'message': 'Match has started'
        }), 400

    match = session.query(Match).filter(Match.matchid == data['matchid'])[0]

    penalty_winners = 1
    if match.is_knockout:
        if 'penalty_winners' in data:
            penalty_winners = data['penalty_winners']
        else:
            return jsonify({
                'success': False,
                'message': 'Must specify field \'penalty_winners\''
            }), 400

    winner = 1
    if data['team_one_pred'] < data['team_two_pred']:
        winner = 2
    elif data['team_one_pred'] == data['team_two_pred']:
        winner = penalty_winners

    prediction = Prediction(
        userid=userid,
        matchid=data['matchid'],
        team_one_pred=data['team_one_pred'],
        team_two_pred=data['team_two_pred'],
        team_to_progress=winner,
        penalty_winners=penalty_winners,
    )

    try:
        session.add(prediction)
        session.flush()

    except SQLAlchemyError as sql_error:
        session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error creating prediction',
            'error': str(sql_error)
        }), 502

    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error creating prediction',
            'error': str(e)
        }), 502

    else:
        session.commit()
        return jsonify({
            'success': True,
            'message': 'Prediction Created',
        })


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


@predictions.route('/prediction', methods=['GET'])
@auth_required
def getPrediction(userid):

    predictions = session.query(Prediction).filter(
        Prediction.userid == userid)

    predictions_formated = []
    for prediction in predictions:
        predictions_formated.append(object_as_dict(prediction))

    return jsonify({
        'success': True,
        'predictions': predictions_formated
    })


def update_prediction(userid, data):
    prediction = session.query(Prediction).filter(
        Prediction.matchid == data['matchid']).filter(Prediction.userid == userid)[0]

    for key, value in data.items():
        if key in ['penalty_winners', 'team_one_pred', 'team_two_pred'] and value is not None:
            setattr(prediction, key, value)

    winner = 1
    team_one_pred = prediction.team_one_pred
    team_two_pred = prediction.team_two_pred
    penalty_winners = prediction.penalty_winners
    if team_one_pred < team_two_pred:
        winner = 2
    elif team_one_pred == team_two_pred:
        winner = penalty_winners

    prediction.team_to_progress = winner

    session.commit()


@predictions.route('/prediction', methods=['DELETE'])
@auth_required
def deletePrediction(userid):

    data = request.get_json()

    session.query(Prediction).filter(
        Prediction.predictionid == data['predictionid']).delete()

    session.commit()

    return jsonify({
        'success': True,
    })


def has_prediction(match, userid):
    already = session.query(exists().where(
        Prediction.userid == userid).where(Prediction.matchid == match.matchid)).scalar()

    return already


def format_matches(matches, userid):
    results = []

    for match in matches:
        hasPrediction = has_prediction(match, userid)
        matchid = match.matchid

        team_one_id = match.team_one_id
        team_two_id = match.team_two_id

        team_one = session.query(Team).filter(Team.teamid == team_one_id)[0]
        team_two = session.query(Team).filter(Team.teamid == team_two_id)[0]

        timezone = pytz.timezone('Europe/London')
        match_time = match.match_datetime
        match_time = match_time.replace(tzinfo=pytz.utc).astimezone(timezone)

        match_formated = {
            "team_one": {
                "name": team_one.name,
                "emoji": team_one.emoji
            },
            "team_two": {
                "name": team_two.name,
                "emoji": team_two.emoji
            },
            "match": {
                "match_date": match_time.strftime("%d"),
                "kick_off_time": match_time.strftime("%H:%M"),
                "is_knockout": match.is_knockout,
                "team_one_goals": match.team_one_goals,
                "team_two_goals": match.team_two_goals,
                "matchid": matchid
            },
            "hasPrediction": hasPrediction,
        }

        if hasPrediction:
            prediction = session.query(Prediction).filter(
                Prediction.userid == userid).filter(Prediction.matchid == matchid)[0]

            match_formated['prediction'] = {
                "team_one_pred": prediction.team_one_pred,
                "team_two_pred": prediction.team_two_pred,
                "predictionid": prediction.predictionid,
                "score": prediction.score,
            }

        results.append(match_formated)
    return results


@ predictions.route('/prediction-required', methods=['GET'])
@ auth_required
def getUnpredictedMatches(userid):

    timezone = pytz.timezone('Europe/London')
    now = datetime.now(timezone)
    today = datetime(now.year, now.month, now.day)

    tomorrow = today + timedelta(2)

    matches = session.query(Match).filter(
        Match.match_datetime >= now).filter(Match.match_datetime <= tomorrow).order_by(Match.match_datetime.asc()).all()

    results = format_matches(matches, userid)

    return jsonify({
        "success": True,
        "matches": results
    })
