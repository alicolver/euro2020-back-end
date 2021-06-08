from flask import Blueprint, jsonify, request
from sqlalchemy.sql import exists
from sqlalchemy import inspect
from database.connection_manager import Session
from blueprints.authentication import auth_required
from database.orm import Prediction
from sqlalchemy.exc import SQLAlchemyError

session = Session()


predictions = Blueprint('predictions', __name__)


@predictions.route('/prediction', methods=['POST'])
@auth_required
def createPrediction(userid):

    data = request.get_json()

    already = session.query(exists().where(
        Prediction.userid == userid and Prediction.matchid == data.matchid)).scalar()

    if already:
        return jsonify({
            'success': False,
            'message': 'Prediction already exists'
        }), 409

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

    predictionid = request.args.get('predictionid')

    already = session.query(exists().where(
        Prediction.predictionid == predictionid)).scalar()

    if not already:
        return jsonify({
            'success': False,
            'message': 'Prediction does not exist'
        }), 404

    prediction = session.query(Prediction).filter(
        Prediction.predictionid == predictionid)[0]

    return jsonify({
        'success': True,
        'prediction': object_as_dict(prediction)
    })


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
