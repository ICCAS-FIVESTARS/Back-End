from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, nullable=True)

    results = relationship("GameResult", back_populates="user")

class GameResult(Base):
    __tablename__ = "game_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stage_number = Column(Integer)
    result_text = Column(String)
    emotion = Column(String)
    emotion_confidence = Column(Float)

    user = relationship("User", back_populates="results")
