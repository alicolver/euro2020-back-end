from flask import Blueprint, jsonify, request
from sqlalchemy.sql import exists
from sqlalchemy.orm import aliased
from database.connection_manager import Session
from blueprints.authentication import admin_required, auth_required
from database.orm import Match, Prediction, Team
from blueprints.predictions import check_kicked_off, object_as_dict
import pytz
from datetime import datetime, timedelta, time
from utils.query import getFullMatchQuery, getUsersMissingGame, getAllUsersPredictions
from utils.format import format_matches
session = Session()


matches = Blueprint('matches', __name__)


@matches.route('/match/ended', methods=['get'])
@auth_required
def endedMatches(userid):
    query = getFullMatchQuery(session, userid)

    matches = query.filter(Match.is_fulltime).order_by(
        Match.match_datetime.desc()).all()

    results = format_matches(matches, userid)
    return jsonify({
        "success": True,
        "matches": results,
    })


@matches.route('/match/test', methods=['get'])
@auth_required
def endedMatchesTest(userid):
    getAllUsersPredictions(session, userid)
    return jsonify({
        "success": True,
    })


@ matches.route('/match/in-progress', methods=['get'])
@ auth_required
def getLiveGames(userid):
    timezone = pytz.timezone('Europe/London')
    now = datetime.now(timezone)
    today = datetime(now.year, now.month, now.day)

    tomorrow = today + timedelta(1)

    query = getFullMatchQuery(session, userid)

    matches = query.filter(Match.match_datetime < now).filter(
        Match.is_fulltime == False).all()

    results = format_matches(matches, userid)

    return jsonify({
        "success": True,
        "matches": results
    })


@ matches.route('/match/end', methods=['put'])
@ admin_required
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

    match.is_fulltime = True

    session.commit()

    return jsonify({
        'success': True,
        'message': 'Match ended'
    })
