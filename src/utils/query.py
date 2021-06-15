from sqlalchemy.orm import aliased
from database.orm import Match, Prediction, Team, User
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from sqlalchemy import true, and_, desc
import pytz


def getFullMatchQuery(session, userid):
    team_one = aliased(Team)
    team_two = aliased(Team)

    sub = session.query(Prediction).filter(
        Prediction.userid == userid).subquery().alias("predictions")

    predict_sub = aliased(Prediction, sub, name="predictions")

    return session.query(Match, team_one, team_two, predict_sub).join(
        team_one, Match.team_one_id == team_one.teamid).join(
        team_two, Match.team_two_id == team_two.teamid).join(
        predict_sub, predict_sub.matchid == Match.matchid, isouter=True)


def getMatchWithoutPrediction(session):
    team_one = aliased(Team)
    team_two = aliased(Team)

    return session.query(Match, team_one, team_two, User).join(
        team_one, Match.team_one_id == team_one.teamid).join(
        team_two, Match.team_two_id == team_two.teamid).join(
        User, true(), isouter=True).join(
        Prediction, and_(User.userid == Prediction.userid,
                         Match.matchid == Prediction.matchid), isouter=True).filter(
            Prediction.predictionid == None).filter(
        User.hidden == False)


def getUsersMissingGame(session):
    timezone = pytz.timezone('Europe/London')
    now = datetime.now(timezone)
    hour = now + timedelta(hours=1)

    query = getMatchWithoutPrediction(session)

    return query.filter(Match.match_datetime > now).filter(
        Match.match_datetime < hour)


def getAllUsersPredictions(session):
    return session.query(
        User.userid.label("userid"),
        User.name.label("name"),
        func.sum(Prediction.score).label("score"),
        func.count(1).filter(Prediction.correct_result).label(
            "correct_results"),
        func.count(1).filter(Prediction.correct_score).label(
            "correct_scores"),
    ).select_from(User).join(Prediction).filter(User.hidden == False).group_by(User.userid).order_by(desc("score"))


def getMatchMissingPredictions(session, matchid):
    query = getMatchWithoutPrediction(session)
    return query.filter(Match.matchid == matchid)
