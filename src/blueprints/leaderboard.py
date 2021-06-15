from flask import Blueprint, jsonify, request
from sqlalchemy.sql import exists
from database.connection_manager import Session
from database.orm import User
from blueprints.authentication import auth_required
from blueprints.score import calculate_user_score
from utils.query import getAllUsersPredictions
from utils.format import format_users
session = Session()


leaderboard = Blueprint('leaderboard', __name__)


@leaderboard.route('/leaderboard', methods=['GET'])
@auth_required
def getLeaderboard(userid):
    users = getAllUsersPredictions(session).all()

    return jsonify({
        "success": True,
        "leaderboard": format_users(users, userid)
    })
