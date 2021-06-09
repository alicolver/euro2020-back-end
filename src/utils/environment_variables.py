import os

POSTGRES_URL = os.environ["POSTGRES_URL"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PW = os.environ["POSTGRES_PASSWORD"]
POSTGRES_DB = os.environ["POSTGRES_DB"]

JWT_KEY = os.environ["SECRET_KEY"]
JWT_ALGORITHM = 'HS256'

# EMAIL_PASSWORD = os.environ["PAGE_NO_REPLY_PASSWORD"]
