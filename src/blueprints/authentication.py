import jwt
import numbers
import math
import random
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from database.orm import PageupUser, PageupPasswordReset
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from utils.users import get_userid, reset_password_email
from utils.environment_variables import JWT_ALGORITHM, JWT_KEY
from passlib.hash import pbkdf2_sha256
from database.conneciton_manager import Session

session = Session()


authentication = Blueprint('authentication', __name__)


@authentication.route('/login', methods=['POST'])
def login():
    credentials = request.get_json()

    error_return = jsonify({
        'token': '',
        'error-message': 'Incorrect Email or Password',
    })

    email = credentials['email']
    password = credentials['password']

    try:
        user = session.query(PageupUser).filter(PageupUser.email == email)[0]

    except Exception as e:
        print(e)
        return error_return

    if not (user and user.check_password(password)):
        return error_return

    payload = {
        'user_id': user.userid,
    }

    jwt_token = jwt.encode(payload, JWT_KEY, JWT_ALGORITHM)

    return jsonify({
        'token': jwt_token.decode('utf-8'),
        'error-message': '',
    })


@authentication.route('/signup', methods=['POST'])
def signup():
    user_info = request.get_json()

    user = PageupUser(
        name=user_info['name'],
        age=user_info['age'],
        email=user_info['email'],
        gender=user_info['gender'],
        postcode=user_info['postcode']
    )

    user.set_password(user_info['password'])

    try:
        session.add(user)
        session.flush()

    except SQLAlchemyError as sql_error:
        session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error processing singup',
            'error': str(sql_error)
        })

    except Exception as e:
        session.rollback()
        return jsonify({
            'success': False,
            'message': 'Error processing singup',
            'error': str(e)
        })

    else:
        session.commit()
        return jsonify({
            'success': True,
            'message': '',
        })


@authentication.route('/validateToken', methods=["GET"])
def validateToken():
    userid = get_userid(request.headers['Authenticate'])

    if isinstance(userid, numbers.Number):
        return jsonify({
            'success': True
        })

    return jsonify({
        'success': False
    })


@authentication.route('/requestPasswordReset', methods=["POST"])
def request_reset():
    try:
        email = request.get_json()["email"]

        user_query = session.query(PageupUser).filter(PageupUser.email == email) 

        if not user_query[0]:
            return jsonify({
                'success': False,
                'error': 'email',
                'message': '',
            })

        random_sequence = [str(math.floor(random.random() * 10)) for _ in range(6)]
        otp = ''.join(random_sequence)

        hashed_otp = pbkdf2_sha256.hash(otp)

        expiry = datetime.now() + timedelta(hours=4)

        passwordResetEntry = PageupPasswordReset(email=email, one_time_password=hashed_otp, expiry_time=expiry, has_reset=False)

        reset_password_email(otp, user_query[0].email, user_query[0].name)

        session.add(passwordResetEntry)
        session.flush()

    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'error': 'unknown',
            'message': str(e),
        })

    else:
        session.commit()
        return jsonify({
            'success': True,
            'error': 'none',
            'message': '',
        })


@authentication.route('/resetPassword', methods=["POST"])
def reset_password():
    try:
        request_json = request.get_json()

        email = request_json["email"]
        new_password = request_json["password"]
        one_time_password = request_json["otp"]

        user = session.query(PageupUser).filter(PageupUser.email == email)[0]

        passwordResetInfo = session.query(PageupPasswordReset).filter(PageupPasswordReset.email == email).order_by(
            desc(PageupPasswordReset.expiry_time))[0]

        if (passwordResetInfo.expiry_time < datetime.now()):
            return jsonify({
                'success': False,
                'message': 'expired'
            })

        if not pbkdf2_sha256.verify(one_time_password, passwordResetInfo.one_time_password):
            return jsonify({
                'success': False,
                'message': 'otp'
            })

        passwordResetInfo.has_reset = True
        user.set_password(new_password)

    except Exception as e:
        print(e)
        session.rollback()
        return jsonify({
            'success': False,
            'message': 'unknown'
        })

    else:
        session.commit()
        return jsonify({
            'success': True
        })