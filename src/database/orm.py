from sqlalchemy import ARRAY, Column, DateTime, Float, Integer, String, Text, text, Boolean, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import INTEGER
from passlib.hash import pbkdf2_sha256


Base = declarative_base()
metadata = Base.metadata

class User(Base):
    __tablename__ = 'users'

    userid = Column(Integer, primary_key=True, server_default=text("nextval('users_userid_seq'::regclass)"))
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    total_score = Column(Integer, nullable=False)

    def set_password(self, password):
        self.password = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)


class Match(Base):
    __tablename__ = 'matches'

    matchid = Column(Integer, primary_key=True, server_default=text("nextval('matches_matchid_seq'::regclass)"))
    team_one = Column(Integer, nullable=False)
    team_two = Column(Integer, nullable=False)
    team_one_goals = Column(Integer)
    team_two_goals = Column(Integer)
    is_fulltime = Column(Boolean)
    match_date = Column(Date, nullable=False)
    kick_off_time = Column(Time, nullable=False)
    is_knockout = Column(Boolean, nullable=False)

class Team(Base):
    __tablename__ = 'teams'

    teamid = Column(Integer, primary_key=True, server_default=text("nextval('teams_teamid_seq'::regclass)"))
    name = Column(Text, nullable=False)
    emoji = Column(Text, nullable=False)

class Prediction(Base):
    __tablename__ = 'predictions'

    userid = Column(Integer, primary_key=True)
    matchid = Column(Integer, primary_key=True)
    team_one_pred = Column(Integer, nullable=False)
    team_two_pred = Column(Integer, nullable=False)
    team_to_progress = Column(Integer, nullable=False)
    penalty_winners = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
