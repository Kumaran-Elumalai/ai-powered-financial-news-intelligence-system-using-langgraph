# src/db/crud.py

from sqlalchemy.orm import Session
from src.db import models

def upsert_article(db: Session, doc: dict):
    """
    Insert or update an article and its entities + impacts.
    """
    article = db.query(models.Article).filter(
        models.Article.id == doc["id"]
    ).first()

    if not article:
        article = models.Article(id=doc["id"])
        db.add(article)

    # Update fields
    article.story_id = str(doc.get("story_id"))
    article.title = doc.get("title")
    article.description = doc.get("description")
    article.url = doc.get("url")
    article.source = doc.get("source")
    article.published = doc.get("published")

    # Clear old entities + impacts (safe upsert)
    db.query(models.Entity).filter(
        models.Entity.article_id == article.id
    ).delete()

    db.query(models.Impact).filter(
        models.Impact.article_id == article.id
    ).delete()

    # Insert new entities
    for e in doc.get("entities", []):
        ent = models.Entity(
            article_id=article.id,
            text=e.get("text"),
            label=e.get("label"),
            source=e.get("source"),
        )
        db.add(ent)

    # Insert new impacts
    for imp in doc.get("impacts", []):
        im = models.Impact(
            article_id=article.id,
            ticker=imp.get("ticker"),
            company=imp.get("company"),
            confidence=imp.get("confidence"),
            impact_type=imp.get("type"),
        )
        db.add(im)

    db.commit()
    return article
