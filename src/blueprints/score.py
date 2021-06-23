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

    if match.is_knockout:
        recalculate_scores_knockout(match, session)
    else:
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


def recalculate_scores_knockout(match, session):
    predictions = session.query(Prediction).filter(
        Prediction.matchid == match.matchid)

    team_one_goals = match.team_one_goals
    team_two_goals = match.team_two_goals
    penalty_winners = match.penalty_winners

    for prediction in predictions:
        team_one_pred = prediction.team_one_pred
        team_two_pred = prediction.team_two_pred
        pen_pred = prediction.penalty_winners
        score = 0
        prediction.correct_score = False
        prediction.correct_result = False

        if match.is_fulltime and team_one_goals == team_two_goals and penalty_winners == pen_pred:
            print("You got pens correct")
            score += 1
        else:
            print("You got pens wrong!")

        if team_one_goals > team_two_goals and team_one_pred > team_two_pred:
            score += 1
            prediction.correct_result = True

        if team_one_goals < team_two_goals and team_one_pred < team_two_pred:
            score += 1
            prediction.correct_result = True

        if team_one_goals == team_two_goals and team_one_pred == team_two_pred:
            score += 1
            prediction.correct_result = True

        team_one_correct = team_one_goals == team_one_pred
        team_two_correct = team_two_goals == team_two_pred
        if team_one_correct:
            score += 1
        if team_two_correct:
            score += 1
        if team_one_correct and team_two_correct:
            prediction.correct_score = True
            score += 1
        print("Final score is", score)
        prediction.score = score
