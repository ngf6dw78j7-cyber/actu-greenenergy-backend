"""
Collecteur RSS — à exécuter périodiquement (cron / tâche planifiée).
Récupère les flux des sources actives, déduplique et insère les nouveaux
articles en base. Le résumé et la catégorisation automatiques (IA) sont
laissés en points d'extension : cf. summarize_and_classify().
"""
import hashlib
import feedparser
from datetime import datetime
from database import SessionLocal
import models


def make_hash(source_name: str, title: str) -> str:
    return hashlib.sha256(f"{source_name}:{title}".encode("utf-8")).hexdigest()


def summarize_and_classify(title: str, content: str):
    """
    Point d'extension IA :
    - Appeler un modèle (ex. l'API Anthropic) pour résumer le contenu
      et déduire la catégorie (Solaire, Éolien, Hydro...) et la région.
    - Retourne (résumé, catégorie, région) ; ici, valeurs par défaut.
    """
    return content[:280] if content else None, None, None


def collect():
    db = SessionLocal()
    try:
        sources = db.query(models.Source).filter(
            models.Source.is_active == True,
            models.Source.rss_feed_url.isnot(None),
        ).all()

        new_count = 0
        for source in sources:
            feed = feedparser.parse(source.rss_feed_url)

            for entry in feed.entries:
                title = entry.get("title", "").strip()
                if not title:
                    continue

                content_hash = make_hash(source.name, title)
                exists = db.query(models.Article).filter_by(content_hash=content_hash).first()
                if exists:
                    continue

                raw_content = entry.get("summary", "")
                summary, category_name, region_name = summarize_and_classify(title, raw_content)

                category = db.query(models.Category).filter_by(name=category_name).first() if category_name else None
                region = db.query(models.Region).filter_by(name=region_name).first() if region_name else None

                published_at = None
                if entry.get("published_parsed"):
                    published_at = datetime(*entry.published_parsed[:6])

                article = models.Article(
                    source_id=source.id,
                    category_id=category.id if category else None,
                    region_id=region.id if region else None,
                    title=title,
                    original_url=entry.get("link", ""),
                    summary=summary,
                    raw_content=raw_content,
                    published_at=published_at,
                    content_hash=content_hash,
                )
                db.add(article)
                new_count += 1

        db.commit()
        print(f"Collecte terminée : {new_count} nouvel(le)(s) article(s).")
    finally:
        db.close()


if __name__ == "__main__":
    collect()
