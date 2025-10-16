from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    interests = Column(JSON)  # 存储列表如 ["technology", "sports"]
    location = Column(String(100))
    device = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    category = Column(String(50))
    keywords = Column(JSON)
    target_age_min = Column(Integer)
    target_age_max = Column(Integer)
    target_gender = Column(String(10))
    bid_price = Column(Float)
    image_url = Column(String(500))
    landing_page = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


class UserInteraction(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)
    ad_id = Column(String(50), index=True, nullable=False)
    action = Column(String(20))  # click, view, purchase, etc.
    timestamp = Column(DateTime, default=func.now())
    context = Column(JSON)  # 额外上下文信息


class UserEmbedding(Base):
    __tablename__ = "user_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    embedding_vector = Column(Text)  # 存储JSON格式的嵌入向量
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())