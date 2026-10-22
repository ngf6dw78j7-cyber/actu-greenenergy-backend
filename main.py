from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import models
from database import engine, get_db
from schemas import ArticleOut

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Actu-GreenEnergy API")

# Autoriser le frontend (à restreindre au vrai domaine en production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/news", response_model=list[ArticleOut])
def get_news(
    category: Optional[str] = None,
    region: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(30, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(models.Article).filter(models.Article.is_published == True)

    if category and category != "Toutes":
        query = query.join(models.Category).filter(models.Category.name == category)

    if region and region != "Monde":
        query = query.join(models.Region).filter(models.Region.name == region)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(models.Article.title.ilike(like), models.Article.summary.ilike(like))
        )

    articles = query.order_by(models.Article.published_at.desc()).limit(limit).all()

    return [
        ArticleOut(
            id=a.id,
            title=a.title,
            original_url=a.original_url,
            summary=a.summary,
            image_url=a.image_url,
            category=a.category_id and db.query(models.Category).get(a.category_id).name,
            region=a.region_id and db.query(models.Region).get(a.region_id).name,
            source=a.source_id and db.query(models.Source).get(a.source_id).name,
            published_at=a.published_at,
        )
        for a in articles
    ]


@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


@app.get("/api/regions")
def get_regions(db: Session = Depends(get_db)):
    return db.query(models.Region).all()


@app.get("/")
def root():
    return {"status": "ok", "service": "Actu-GreenEnergy API"}
