from sqlalchemy import ARRAY, Column, DateTime, Float, Integer, String, Text, text, Boolean, Date, Time, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import INTEGER
from passlib.hash import pbkdf2_sha256


Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = 'users'

    userid = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    admin = Column(Boolean, nullable=False, default=False)
    hidden = Column(Boolean, nullable=False, default=False)

    def set_password(self, password):
        self.password = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

class PasswordReset(Base):
    __tablename__ = 'passwordreset'

    email = Column(String(255), nullable=False, primary_key=True)
    one_time_password = Column(String(255), nullable=False)
    expiry_time = Column(DateTime, nullable=False, primary_key=True)
    has_reset = Column(Boolean, nullable=False, default=False)

    def set_password(self, password):
        self.password = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

class Team(Base):
    __tablename__ = 'teams'

    teamid = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    emoji = Column(Text, nullable=False)


class Match(Base):
    __tablename__ = 'matches'

    matchid = Column(Integer, primary_key=True)
    team_one_id = Column(Integer, ForeignKey('teams.teamid'))
    team_two_id = Column(Integer, ForeignKey('teams.teamid'))
    team_one_goals = Column(Integer)
    team_two_goals = Column(Integer)
    is_fulltime = Column(Boolean)
    match_date = Column(Date, nullable=False)
    kick_off_time = Column(Time, nullable=False)
    is_knockout = Column(Boolean, nullable=False)
    team_one = relationship("Team", foreign_keys=[team_one_id])
    team_two = relationship("Team", foreign_keys=[team_two_id])


class Prediction(Base):
    __tablename__ = 'predictions'
    predictionid = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('users.userid'))
    matchid = Column(Integer, ForeignKey('matches.matchid'))
    team_one_pred = Column(Integer, nullable=False)
    team_two_pred = Column(Integer, nullable=False)
    team_to_progress = Column(Integer, nullable=False)
    penalty_winners = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False, default=0)
    correct_result = Column(Boolean, nullable=False, default=False)
    correct_score = Column(Boolean, nullable=False, default=False)
    score = Column(Integer, nullable=False, default=0)
    user = relationship("User", foreign_keys=[userid])
    match = relationship("Match", foreign_keys=[matchid])
