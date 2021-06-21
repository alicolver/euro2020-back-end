import pytz
from sqlalchemy import inspect


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


def format_match(match):
    timezone = pytz.timezone('Europe/London')
    match_time = match.match_datetime
    match_time = match_time.replace(tzinfo=pytz.utc).astimezone(timezone)
    return {
        "match_date": match_time.strftime("%d"),
        "kick_off_time": match_time.strftime("%H:%M"),
        "match_datetime": match_time,
        "is_knockout": match.is_knockout,
        "team_one_goals": match.team_one_goals,
        "team_two_goals": match.team_two_goals,
        "matchid": match.matchid
    }


def format_team(team):
    return {
        "name": team.name,
        "emoji": team.emoji
    }


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
            "team_one": format_team(team_one),
            "team_two": format_team(team_two),
            "match": format_match(match),
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
        form_pred = object_as_dict(pred[0])
        form_pred['name'] = pred[1].name
        formated_preds.append(form_pred)
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


def format_missing_predictions(rows):
    # (Match, team_one, team_two, User)
    matchid_to_match = {}
    for row in rows:
        match = row[0]
        user = {
            'name': row[3].name,
            'userid': row[3].userid,
        }
        if match.matchid in matchid_to_match:
            matchid_to_match[match.matchid]['users'].append(user)
        else:
            matchid_to_match[match.matchid] = {
                'match': format_match(match),
                'team_one': format_team(row[1]),
                'team_two': format_team(row[2]),
                'users': [user],
            }
    formated = []
    for matchid, data in matchid_to_match.items():
        data['users'] = sorted(data['users'], key=lambda user: user['name'])
        formated.append(data)

    return sorted(formated, key=lambda data: data['match']['match_datetime'])
