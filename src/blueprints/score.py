from datetime import timedelta
import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy.sql import exists
from database.connection_manager import Session
from blueprints.authentication import admin_required
from database.orm import Match, Prediction
from blueprints.predictions import check_kicked_off

session = Session()


scores = Blueprint('scores', __name__)


@scores.route('/score', methods=['put'])
@admin_required
def setScore():
    data = request.get_json()

    already = session.query(exists().where(
        Match.matchid == data['matchid'])).scalar()

    if not already:
        return jsonify({
            'success': False,
            'message': 'Match does not exist'
        }), 404

    match = session.query(Match).filter(
        Match.matchid == data['matchid'])[0]

    match.team_one_goals = data['team_one_goals']
    match.team_two_goals = data['team_two_goals']

    recalculate_scores(match)

    session.commit()

    return jsonify({
        'success': True,
        'message': 'Score updated'
    })


def recalculate_scores(match):
    predictions = session.query(Prediction).filter(
        Prediction.matchid == match.matchid)

    team_one_goals = match.team_one_goals
    team_two_goals = match.team_two_goals

    for prediction in predictions:
        team_one_pred = prediction.team_one_pred
        team_two_pred = prediction.team_two_pred

        if team_one_goals == team_one_pred and team_two_goals == team_two_pred:
            prediction.score = 3
            prediction.correct_score = True
            prediction.correct_result = True
            continue

        if team_one_goals > team_two_goals and team_one_pred > team_two_pred:
            prediction.score = 1
            prediction.correct_score = False
            prediction.correct_result = True
            continue

        if team_one_goals < team_two_goals and team_one_pred < team_two_pred:
            prediction.score = 1
            prediction.correct_score = False
            prediction.correct_result = True
            continue

        if team_one_goals == team_two_goals and team_one_pred == team_two_pred:
            prediction.score = 1
            prediction.correct_score = False
            prediction.correct_result = True
            continue

        prediction.score = 0
        prediction.correct_score = False
        prediction.correct_result = False


def calculate_user_score(user):
    predictions = session.query(Prediction).filter(
        Prediction.userid == user.userid)
    score = 0
    correct_results = 0
    correct_scores = 0
    for prediction in predictions:
        score += prediction.score
        if prediction.correct_score:
            correct_scores += 1

        if prediction.correct_result:
            correct_results += 1
    return score, correct_scores, correct_results
