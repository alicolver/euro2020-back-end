import os

POSTGRES_URL = os.environ["POSTGRES_URL"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PW = os.environ["POSTGRES_PASSWORD"]
POSTGRES_DB = os.environ["POSTGRES_DB"]

JWT_KEY = os.environ["SECRET_KEY"]
JWT_ALGORITHM = 'HS256'

EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
EMAIL_USERNAME = os.environ['EMAIL_USERNAME']
EMAIL_PORT = 465
EMAIL_SERVER = 'smtp.gmail.com'

PRIV_KEY = os.environ['PRIV_KEY']

HIDE_KNOCKOUTS = os.environ['HIDE_KNOCKOUTS'] == 'True' if 'HIDE_KNOCKOUTS' in os.environ else False
