import uuid
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base


class Source(Base):
    __tablename__ = "sources"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    url = Column(Text, nullable=False)
    rss_feed_url = Column(Text)
    type = Column(String(50), default="rss")
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    emoji = Column(String(10))


class Region(Base):
    __tablename__ = "regions"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    parent_region_id = Column(Integer, ForeignKey("regions.id"))


class Article(Base):
    __tablename__ = "articles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    region_id = Column(Integer, ForeignKey("regions.id"))

    title = Column(String(500), nullable=False)
    original_url = Column(Text, nullable=False)
    summary = Column(Text)
    raw_content = Column(Text)
    image_url = Column(Text)

    published_at = Column(TIMESTAMP(timezone=True))
    collected_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    content_hash = Column(String(64), unique=True)
    is_published = Column(Boolean, default=True)
