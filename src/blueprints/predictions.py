from flask import Blueprint, jsonify, request
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

    kick_off = getattr(match, 'kick_off_time')
    match_date = getattr(match, 'match_date')

    combined = datetime.combine(match_date, kick_off)
    combined = timezone.localize(combined)

    current_time = datetime.now(timezone)

    return combined < current_time


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

    winner = 1
    if data['team_one_pred'] < data['team_two_pred']:
        winner = 2
    elif data['team_one_pred'] == data['team_two_pred']:
        winner = data['penalty_winners']

    prediction = Prediction(
        userid=userid,
        matchid=data['matchid'],
        team_one_pred=data['team_one_pred'],
        team_two_pred=data['team_two_pred'],
        team_to_progress=winner,
        penalty_winners=data['penalty_winners'],
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
        if key in ['penalty_winners', 'team_one_pred', 'team_two_pred']:
            setattr(prediction, key, value)

    winner = 1
    team_one_pred = getattr(prediction, 'team_one_pred')
    team_two_pred = getattr(prediction, 'team_two_pred')
    penalty_winners = getattr(prediction, 'penalty_winners')
    if team_one_pred < team_two_pred:
        winner = 2
    elif team_one_pred == team_two_pred:
        winner = penalty_winners

    setattr(prediction, 'team_to_progress', winner)

    session.commit()


@predictions.route('/prediction', methods=['PUT'])
@auth_required
def updatePrediction(userid):

    data = request.get_json()

    already = session.query(exists().where(
        Prediction.predictionid == data['predictionid'])).scalar()

    if not already:
        return jsonify({
            'success': False,
            'message': 'Prediction does not exist'
        }), 404

    prediction = session.query(Prediction).filter(
        Prediction.predictionid == data['predictionid'])[0]

    matchid = getattr(prediction, 'matchid')
    if check_kicked_off(matchid):
        return jsonify({
            'success': False,
            'message': 'Match has started'
        }), 400

    for key, value in data['prediction'].items():
        if key in ['penalty_winners', 'team_one_pred', 'team_two_pred']:
            setattr(prediction, key, value)

    winner = 1
    team_one_pred = getattr(prediction, 'team_one_pred')
    team_two_pred = getattr(prediction, 'team_two_pred')
    penalty_winners = getattr(prediction, 'penalty_winners')
    if team_one_pred < team_two_pred:
        winner = 2
    elif team_one_pred == team_two_pred:
        winner = penalty_winners

    setattr(prediction, 'team_to_progress', winner)

    session.commit()

    return jsonify({
        'success': True,
        'prediction': object_as_dict(prediction)
    })


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
        Prediction.userid == userid).where(Prediction.matchid == getattr(match, 'matchid'))).scalar()

    return already


@ predictions.route('/prediction-required', methods=['GET'])
@ auth_required
def getUnpredictedMatches(userid):

    timezone = pytz.timezone('Europe/London')
    today = datetime.today()
    today = datetime(today.year, today.month, today.day)

    tomorrow = today + timedelta(1)

    matches = session.query(Match).filter(
        Match.match_date >= today).filter(Match.match_date <= tomorrow).all()

    results = []

    for match in matches:
        hasPrediction = has_prediction(match, userid)
        matchid = getattr(match, 'matchid')
        if check_kicked_off(matchid):
            continue

        team_one_id = getattr(match, 'team_one_id')
        team_two_id = getattr(match, 'team_two_id')

        team_one = session.query(Team).filter(Team.teamid == team_one_id)[0]
        team_two = session.query(Team).filter(Team.teamid == team_two_id)[0]

        match_formated = {
            "team_one": {
                "name": getattr(team_one, 'name'),
                "emoji": getattr(team_one, 'emoji')
            },
            "team_two": {
                "name": getattr(team_two, 'name'),
                "emoji": getattr(team_two, 'emoji')
            },
            "match": {
                "match_date": getattr(match, 'match_date').isoformat(),
                "kick_off_time": getattr(match, 'kick_off_time').isoformat(),
                "is_knockout": getattr(match, 'is_knockout'),
                "matchid": matchid
            },
            "hasPrediction": hasPrediction,
        }

        if hasPrediction:
            prediction = session.query(Prediction).filter(
                Prediction.userid == userid).filter(Prediction.matchid == matchid)[0]

            match_formated['prediction'] = {
                "team_one_pred": getattr(prediction, 'team_one_pred'),
                "team_two_pred": getattr(prediction, 'team_two_pred'),
                "predictionid": getattr(prediction, 'predictionid'),
            }

        results.append(match_formated)

    return jsonify({
        "success": True,
        "matches": results
    })
