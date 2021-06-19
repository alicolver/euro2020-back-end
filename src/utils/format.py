import pytz
from sqlalchemy import inspect


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


def format_matches(matches, userid):
    results = []

    for row in matches:
        match = row[0]
        team_one = row[1]
        team_two = row[2]
        prediction = row[3]

        hasPrediction = prediction is not None

        timezone = pytz.timezone('Europe/London')
        match_time = match.match_datetime
        match_time = match_time.replace(tzinfo=pytz.utc).astimezone(timezone)

        match_formated = {
            "team_one": {
                "name": team_one.name,
                "emoji": team_one.emoji
            },
            "team_two": {
                "name": team_two.name,
                "emoji": team_two.emoji
            },
            "match": {
                "match_date": match_time.strftime("%d"),
                "kick_off_time": match_time.strftime("%H:%M"),
                "is_knockout": match.is_knockout,
                "team_one_goals": match.team_one_goals,
                "team_two_goals": match.team_two_goals,
                "matchid": match.matchid
            },
            "hasPrediction": hasPrediction,
        }

        if hasPrediction:
            match_formated['prediction'] = {
                "team_one_pred": prediction.team_one_pred,
                "team_two_pred": prediction.team_two_pred,
                "predictionid": prediction.predictionid,
                "score": prediction.score,
            }

        results.append(match_formated)
    return results


def format_predictions(predictions):
    formated_preds = []
    for pred in predictions:
        formated_preds.append(object_as_dict(pred))
    return formated_preds


def format_users(users, userid):
    users_formated = []
    for user in users:
        is_user = user.userid == userid
        user_formated = {
            "name": user.name,
            "userid": user.userid,
            "score": user.score,
            "correct_scores": user.correct_scores,
            "correct_results": user.correct_results,
            "is_user": is_user,
        }
        users_formated.append(user_formated)

    return users_formated
