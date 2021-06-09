from flask import Blueprint, jsonify, request
from sqlalchemy.sql import exists
from database.connection_manager import Session
from database.orm import User
from blueprints.score import calculate_user_score
session = Session()


leaderboard = Blueprint('leaderboard', __name__)


@leaderboard.route('/leaderboard', methods=['GET'])
def getLeaderboard():
    users = session.query(User).all()
    users_formated = []
    for user in users:
        user_formated = {
            "name": getattr(user, 'name'),
            "score": calculate_user_score(user)
        }
        users_formated.append(user_formated)

    ordered = sorted(users_formated, key=lambda u: u['score'])

    return jsonify({
        "success": True,
        "leaderboard": ordered
    })
