from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import random
import os
import uuid
import time

from database import get_db, init_db
from models import Dish, Restaurant, User, UserPreference, Order, RecommendationEvent
from engine import RecommendationEngine

app = FastAPI(title="Surprise Me API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/api/v1/surprise")
def get_surprise(
    session_id: str,
    user_id: str = "default-user", # Mock user for demo
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    dietary: Optional[str] = None,
    spice_level: Optional[int] = None,
    max_eta_minutes: int = 45,
    exclude_cuisines: List[str] = Query([]),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    engine = RecommendationEngine(db)
    
    dish = engine.get_recommendation(
        user_id=user_id,
        session_id=session_id,
        budget_min=budget_min,
        budget_max=budget_max,
        dietary=dietary,
        spice_level=spice_level,
        max_eta=max_eta_minutes,
        exclude_cuisines=exclude_cuisines
    )
    
    if not dish:
        raise HTTPException(status_code=404, detail="No matching dishes found.")

    response_ms = int((time.time() - start_time) * 1000)
    
    # In a real app, we'd fetch actual ETA from a logistics service
    eta = random_eta(dish.restaurant_id) 

    return {
        "dish_id": dish.id,
        "dish_name": dish.name,
        "description": f"Delicious {dish.cuisine} prepared with fresh ingredients.",
        "restaurant": {
            "id": dish.restaurant_id,
            "name": dish.restaurant.name,
            "rating": float(dish.restaurant.rating),
            "reviews": dish.rating_count * 5 # Mock review count
        },
        "price": float(dish.price),
        "currency": "INR",
        "eta_minutes": eta,
        "image_url": dish.image_url or "https://images.unsplash.com/photo-1546069901-ba9599a7e63c",
        "cuisine": dish.cuisine,
        "dietary_tags": dish.dietary_tags,
        "tier": getattr(dish, "selected_tier", "novel"),
        "response_ms": response_ms
    }

@app.post("/api/v1/recommendation-event", status_code=204)
def log_event(event_data: dict, db: Session = Depends(get_db)):
    event = RecommendationEvent(
        user_id="default-user", # Mock user
        dish_id=event_data["dish_id"],
        session_id=event_data["session_id"],
        outcome=event_data["outcome"],
        response_ms=event_data.get("response_ms", 0)
    )
    db.add(event)
    db.commit()
    return

@app.post("/api/v1/auth/send-otp")
async def send_otp(data: dict):
    phone = data.get("phone")
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number required")
    # In a real app, send OTP via SMS. Here we just mock it.
    print(f"OTP for {phone}: 123456")
    return {"status": "success", "message": "OTP sent successfully"}

@app.post("/api/v1/auth/verify-otp")
async def verify_otp(data: dict):
    phone = data.get("phone")
    otp = data.get("otp")
    if phone and otp == "123456": # Simple mock verification
        return {"status": "success", "user": {"id": "default-user", "name": "Lauren White", "phone": phone}}
    raise HTTPException(status_code=400, detail="Invalid OTP")

@app.post("/api/v1/payment/verify")
async def verify_payment(data: dict):
    # Simulation of payment verification
    time.sleep(1.5) # Simulate processing
    payment_id = data.get("payment_id")
    if payment_id:
        return {"status": "success", "message": "Payment verified", "transaction_id": str(uuid.uuid4())}
    raise HTTPException(status_code=400, detail="Invalid payment ID")

def random_eta(restaurant_id):
    import random
    return random.randint(15, 45)

@app.get("/api/v1/categories")
def get_categories():
    return [
        {"id": "momo", "name": "Momo", "icon": "🥟"},
        {"id": "noodles", "name": "Noodles", "icon": "🍜"},
        {"id": "sandwich", "name": "Sandwich", "icon": "🥪"},
        {"id": "burger", "name": "Burger", "icon": "🍔"},
        {"id": "pizza", "name": "Pizza", "icon": "🍕"},
        {"id": "pasta", "name": "Pasta", "icon": "🍝"}
    ]

@app.get("/api/v1/dishes")
def get_dishes(
    category: Optional[str] = None, 
    is_special: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Dish).join(Restaurant).filter(Restaurant.is_open == True)
    if category:
        query = query.filter(Dish.cuisine.ilike(f"%{category}%"))
    if is_special:
        query = query.filter(Dish.rating >= 4.5)
    
    dishes = query.limit(20).all()
    return [{
        "id": d.id,
        "name": d.name,
        "price": float(d.price),
        "rating": float(d.rating),
        "cuisine": d.cuisine,
        "image_url": d.image_url,
        "restaurant_name": d.restaurant.name
    } for d in dishes]

@app.post("/api/v1/orders")
def create_order(order_data: dict, db: Session = Depends(get_db)):
    # Simple order creation for demo
    new_order = Order(
        user_id="default-user",
        dish_id=order_data["items"][0]["id"], # Just link to first dish for simplicity
        restaurant_id=order_data["items"][0].get("restaurant_id", "default-res"),
        amount=order_data["total"],
        status="placed"
    )
    db.add(new_order)
    db.commit()
    return {"status": "success", "order_id": new_order.id}

@app.get("/api/v1/init-data")
def seed_data(db: Session = Depends(get_db)):
    # Create mock user
    user_id = "default-user"
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, name="Lauren White", email="lauren@example.com", city="Baluwatar")
        db.add(user)
        db.commit()
        
        prefs = UserPreference(
            user_id=user_id,
            favourite_cuisines=["Burger", "Pizza"],
            dietary_flags=["veg"],
            budget_min=100,
            budget_max=1500
        )
        db.add(prefs)
        
    # Create mock restaurants and dishes
    indian_categories = [
        {"name": "Biryani", "dishes": [
            {"name": "Hyderabadi Mutton Biryani", "price": 450, "tags": ["non-veg"]},
            {"name": "Chicken Dum Biryani", "price": 350, "tags": ["non-veg"]},
            {"name": "Veg Lucknowi Biryani", "price": 280, "tags": ["veg"]}
        ]},
        {"name": "North Indian", "dishes": [
            {"name": "Butter Chicken", "price": 380, "tags": ["non-veg"]},
            {"name": "Paneer Butter Masala", "price": 320, "tags": ["veg"]},
            {"name": "Dal Makhani", "price": 260, "tags": ["veg"]}
        ]},
        {"name": "South Indian", "dishes": [
            {"name": "Masala Dosa", "price": 120, "tags": ["veg"]},
            {"name": "Paneer Uttapam", "price": 150, "tags": ["veg"]},
            {"name": "Ghee Roast Idli", "price": 90, "tags": ["veg"]}
        ]},
        {"name": "Street Food", "dishes": [
            {"name": "Chole Bhature", "price": 180, "tags": ["veg"]},
            {"name": "Pav Bhaji", "price": 140, "tags": ["veg"]},
            {"name": "Pani Puri (Pack of 12)", "price": 80, "tags": ["veg"]}
        ]},
        {"name": "Tandoori", "dishes": [
            {"name": "Chicken Tandoori Full", "price": 550, "tags": ["non-veg"]},
            {"name": "Paneer Tikka Angara", "price": 290, "tags": ["veg"]},
            {"name": "Soya Chaap Tikka", "price": 240, "tags": ["veg"]}
        ]}
    ]

    for cat in indian_categories:
        res_id = str(uuid.uuid4())
        res = Restaurant(
            id=res_id,
            name=f"The {cat['name']} House",
            city="Baluwatar",
            rating=4.3 + (random.random() * 0.5),
            is_open=True
        )
        db.add(res)
        db.flush()
        
        for dish_data in cat['dishes']:
            dish = Dish(
                restaurant_id=res_id,
                name=dish_data['name'],
                cuisine=cat['name'],
                price=dish_data['price'],
                dietary_tags=dish_data['tags'],
                rating=4.2 + (random.random() * 0.7),
                rating_count=100 + random.randint(0, 500),
                image_url=f"https://source.unsplash.com/600x400/?indian,food,{dish_data['name'].replace(' ', ',')}"
            )
            db.add(dish)
            
    db.commit()
    return {"status": "Database seeded with Zomato-like data"}
