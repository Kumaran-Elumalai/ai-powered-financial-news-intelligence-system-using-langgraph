from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Float
)
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.db import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(String, index=True)
    title = Column(Text)
    description = Column(Text)
    url = Column(String)
    source = Column(String)
    published = Column(String)   # store as original string
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    entities = relationship("Entity", back_populates="article")
    impacts = relationship("Impact", back_populates="article")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    text = Column(String)
    label = Column(String)
    source = Column(String)

    article = relationship("Article", back_populates="entities")


class Impact(Base):
    __tablename__ = "impacts"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    ticker = Column(String, index=True)
    company = Column(String)
    confidence = Column(Float)
    impact_type = Column(String)  # direct, sector, regulatory

    article = relationship("Article", back_populates="impacts")
