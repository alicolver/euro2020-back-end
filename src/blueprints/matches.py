from flask import Blueprint, jsonify, request
from sqlalchemy.sql import exists
from database.connection_manager import Session
from blueprints.authentication import admin_required, auth_required
from database.orm import Match, Prediction, Team
from blueprints.predictions import format_matches
session = Session()


matches = Blueprint('matches', __name__)


@matches.route('/match/ended', methods=['get'])
@auth_required
def endedMatches(userid):
    matches = session.query(Match).filter(Match.is_fulltime).all()

    print(matches)

    results = format_matches(matches, userid)
    print(results)
    return jsonify({
        "success": True,
        "matches": results,
    })
