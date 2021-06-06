from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.environment_variables import POSTGRES_DB, POSTGRES_PW, POSTGRES_USER, POSTGRES_URL

SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pw}@{url}/{db}'\
    .format(user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL, db=POSTGRES_DB)

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)