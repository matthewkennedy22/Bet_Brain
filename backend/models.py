from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Game(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True)
    sport = Column(String, index=True)
    home_team = Column(String)
    away_team = Column(String)
    commence_time = Column(DateTime)
    odds_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class BetPick(Base):
    __tablename__ = "bet_picks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, index=True)
    sport = Column(String)
    pick_type = Column(String)  # moneyline, spread, total
    pick = Column(String)  # Team name or Over/Under
    odds = Column(Integer)
    confidence = Column(Float)
    ev_score = Column(Float)
    reasoning = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    result = Column(String, nullable=True)  # win, loss, push


class NewsItem(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    summary = Column(String)
    source = Column(String)
    sport = Column(String)
    sentiment = Column(Float)
    teams_mentioned = Column(JSON)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

