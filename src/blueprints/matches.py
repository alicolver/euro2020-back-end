from flask import Blueprint, jsonify, request
from sqlalchemy.sql import exists
from sqlalchemy.orm import aliased
from database.connection_manager import Session
from blueprints.authentication import admin_required, auth_required
from database.orm import Match, Prediction, Team
from blueprints.predictions import check_kicked_off
import pytz
from datetime import datetime, timedelta, time
from utils.query import getFullMatchQuery, getUsersMissingGame, getAllUsersPredictions, getMatchMissingPredictions
from utils.format import format_matches, format_predictions, object_as_dict
session = Session()


matches = Blueprint('matches', __name__)


@matches.route('/match/ended', methods=['get'])
@auth_required
def endedMatches(userid):

    if request.args.get("userid") is not None:
        if not request.args.get("userid").isnumeric():
            return jsonify({
                'success': False,
                'message': "userid must be a number",
            }), 404
        userid = request.args.get("userid")

    query = getFullMatchQuery(session, userid)

    matches = query.filter(Match.is_fulltime).order_by(
        Match.match_datetime.desc()).all()

    results = format_matches(matches, userid)
    return jsonify({
        "success": True,
        "matches": results,
    })


@matches.route('/match/missing', methods=['get'])
@admin_required
def matchMissingPredictions():
    matchid = request.args.get('matchid')
    rows = getMatchMissingPredictions(session, matchid).all()
    return jsonify({
        "success": True,
        "users": list(map(lambda r: r[3].name, rows))
    })


@ matches.route('/match/in-progress', methods=['get'])
@ auth_required
def getLiveGames(userid):
    timezone = pytz.timezone('Europe/London')
    now = datetime.now(timezone)
    today = datetime(now.year, now.month, now.day)

    if request.args.get("userid") is not None:
        if not request.args.get("userid").isnumeric():
            return jsonify({
                'success': False,
                'message': "userid must be a number",
            }), 404
        userid = request.args.get("userid")

    tomorrow = today + timedelta(1)

    query = getFullMatchQuery(session, userid)

    matches = query.filter(Match.match_datetime < now).filter(
        Match.is_fulltime == False).all()

    results = format_matches(matches, userid)

    return jsonify({
        "success": True,
        "matches": results
    })


@matches.route('/match/predictions', methods=['GET'])
@auth_required
def getMatchPredictions(userid):
    matchid = request.args.get("matchid")
    print(matchid)

    if matchid is None:
        return jsonify({
            'success': False,
            'message': "You must send a matchid"
        }), 404

    match = session.query(Match).filter(Match.matchid == matchid).all()[0]
    print(match)
    if not check_kicked_off(matchid):
        return jsonify({
            'success': False,
            'message': "Match has not kicked off yet"
        }), 404

    predictions = session.query(Prediction).filter(
        Prediction.matchid == matchid).order_by(Prediction.score.desc()).all()

    return jsonify({
        'success': True,
        'match': object_as_dict(match),
        'predictions': format_predictions(predictions)
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
