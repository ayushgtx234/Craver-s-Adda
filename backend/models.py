from sqlalchemy import Column, String, Boolean, Numeric, Integer, ForeignKey, Text, Table, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    city = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    favourite_cuisines = Column(JSON, default=[]) # Stored as list
    dietary_flags = Column(JSON, default=[]) # 'veg', 'vegan', etc.
    budget_min = Column(Numeric(8, 2), default=50)
    budget_max = Column(Numeric(8, 2), default=500)
    spice_level = Column(Integer, default=2) # 1=mild, 2=medium, 3=hot
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="preferences")

class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    rating = Column(Numeric(3, 2))
    is_open = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    dishes = relationship("Dish", back_populates="restaurant")

class Dish(Base):
    __tablename__ = "dishes"
    id = Column(String, primary_key=True, default=generate_uuid)
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String, nullable=False)
    cuisine = Column(String, nullable=False)
    price = Column(Numeric(8, 2), nullable=False)
    dietary_tags = Column(JSON, default=[])
    spice_level = Column(Integer, default=2)
    image_url = Column(Text)
    rating = Column(Numeric(3, 2))
    rating_count = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    restaurant = relationship("Restaurant", back_populates="dishes")

class Order(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    dish_id = Column(String, ForeignKey("dishes.id"), nullable=False)
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="placed")
    placed_at = Column(DateTime, server_default=func.now())
    delivered_at = Column(DateTime)

    user = relationship("User", back_populates="orders")

class RecommendationEvent(Base):
    __tablename__ = "recommendation_events"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    dish_id = Column(String, ForeignKey("dishes.id"), nullable=False)
    session_id = Column(String, nullable=False)
    filters_applied = Column(JSON)
    outcome = Column(String) # 'ordered' | 'retried' | 'dismissed' | 'saved'
    response_ms = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
