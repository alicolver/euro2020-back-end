from flask import Blueprint, jsonify, request
from sqlalchemy.sql import exists
from database.connection_manager import Session
from blueprints.authentication import admin_required
from database.orm import Match
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

    setattr(match, "team_one_goals", data['team_one_goals'])
    setattr(match, "team_two_goals", data['team_two_goals'])

    # Recalculate scores here?

    session.commit()

    return jsonify({
        'success': True,
        'message': 'Score updated'
    })


@scores.route('/match/end', methods=['post'])
@admin_required
def endMatch():
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

    setattr(match, "is_fulltime", True)

    session.commit()

    return jsonify({
        'success': True,
        'message': 'Match ended'
    })
