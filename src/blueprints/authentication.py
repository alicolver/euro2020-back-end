import jwt
from functools import wraps
import numbers
import math
import random
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta

from sqlalchemy.sql.expression import false
from database.orm import User, PasswordReset
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from utils.users import get_userid
from utils.mail import sendPasswordResetEmail
from utils.environment_variables import JWT_ALGORITHM, JWT_KEY_PRIV
from passlib.hash import pbkdf2_sha256
from database.connection_manager import Session
from utils.time import now

session = Session()


authentication = Blueprint('authentication', __name__)


@authentication.route('/login', methods=['POST'])
def login():
    credentials = request.get_json()

    error_return = jsonify({
        'token': '',
        'error-message': 'Incorrect Email or Password',
        'success': False,
    }), 403

    email = credentials['email'].lower()
    password = credentials['password']

    try:
        user = session.query(User).filter(User.email == email)[0]

    except Exception as e:
        print(e)
        return error_return

    if not (user and user.check_password(password)):
        return error_return

    user.force_login = False
    user.last_login = now()

    session.commit()

    payload = {
        'userid': user.userid,
        'admin': user.admin,
    }

    jwt_token = jwt.encode(payload, JWT_KEY_PRIV, JWT_ALGORITHM)

    return jsonify({
        'token': jwt_token,
        'error-message': '',
        'success': True,
    })


@authentication.route('/signup', methods=['POST'])
def signup():
    user_info = request.get_json()

    user = User(
        name=user_info['name'],
        email=user_info['email'].lower(),
        last_login=now()
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


def auth_required(endpoint):
    @wraps(endpoint)
    def wrapper(*args, **kws):
        token = request.headers.get('Authenticate')
        if token is None:
            return jsonify({
                'success': False
            }), 403

        userid = get_userid(token)

        if not isinstance(userid, numbers.Number):
            return jsonify({
                'success': False
            }), 403

        user = session.query(User).filter(User.userid == userid)[0]
        if user.force_login:
            return jsonify({
                'success': False,
                'message': "Refresh login required"
            }), 403

        return endpoint(userid, *args, **kws)
    return wrapper


def admin_required(endpoint):
    @wraps(endpoint)
    def wrapper(*args, **kws):
        userid = get_userid(request.headers['Authenticate'])

        if not isinstance(userid, numbers.Number):
            return jsonify({
                'success': False
            }), 403

        user = session.query(User).filter(User.userid == userid)[0]

        admin = user.admin

        if not admin:
            return jsonify({
                'success': False
            }), 403

        return endpoint(*args, **kws)
    return wrapper


@authentication.route('/validateToken', methods=["GET"])
@auth_required
def validateToken(userid):
    return jsonify({
        'success': True
    })


@authentication.route('/is-admin', methods=["GET"])
@admin_required
def isAdmin():
    return jsonify({
        'success': True
    })


@authentication.route('/user/name', methods=["GET"])
@auth_required
def getName(userid):
    if request.args.get("userid") is None:
        return jsonify({
            'success': False,
            'message': "Please give a userid",
        }), 404

    if not request.args.get("userid").isnumeric():
        return jsonify({
            'success': False,
            'message': "userid must be a number",
        }), 404

    userid = request.args.get("userid")
    user = session.query(User).filter(User.userid == userid).all()[0]
    return jsonify({
        'success': True,
        'name': user.name,
    })


@authentication.route('/reset-password', methods=["POST"])
def request_reset():
    try:
        email = request.get_json()["email"].lower()

        user_query = session.query(User).filter(User.email == email)

        if not user_query[0]:
            return jsonify({
                'success': False,
                'error': 'email',
                'message': 'User does not exist',
            })

        random_sequence = [str(math.floor(random.random() * 10))
                           for _ in range(6)]
        otp = ''.join(random_sequence)

        hashed_otp = pbkdf2_sha256.hash(otp)

        expiry = datetime.now() + timedelta(hours=4)

        passwordResetEntry = PasswordReset(
            email=email, one_time_password=hashed_otp, expiry_time=expiry, has_reset=False)

        sendPasswordResetEmail(user_query[0].name, user_query[0].email, otp)

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


@authentication.route('/reset-password', methods=["PUT"])
def reset_password():
    try:
        request_json = request.get_json()

        email = request_json["email"]
        new_password = request_json["password"]
        one_time_password = request_json["otp"]

        user = session.query(User).filter(User.email == email)[0]

        passwordResetInfo = session.query(PasswordReset).filter(PasswordReset.email == email).order_by(
            desc(PasswordReset.expiry_time))[0]

        if (passwordResetInfo.has_reset):
            return jsonify({
                'success': False,
                'message': 'OTP already used'
            })

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
            'message': str(e)
        })

    else:
        session.commit()
        return jsonify({
            'success': True,
            'message': 'password updated successfully'
        })
