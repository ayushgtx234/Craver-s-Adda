import random
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Dish, Restaurant, UserPreference, Order, RecommendationEvent

class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_recommendation(
        self, 
        user_id: str, 
        session_id: str,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        dietary: Optional[str] = None,
        spice_level: Optional[int] = None,
        max_eta: int = 45,
        exclude_cuisines: List[str] = []
    ):
        # 1. Fetch User Context
        prefs = self.db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
        
        # Merge filters with preferences
        b_min = budget_min if budget_min is not None else (prefs.budget_min if prefs else 50)
        b_max = budget_max if budget_max is not None else (prefs.budget_max if prefs else 500)
        dietary_flags = [dietary] if dietary else (prefs.dietary_flags if prefs else [])
        
        # 2. Get Recent Recommendations for Deduplication (Last 5)
        recent_events = self.db.query(RecommendationEvent)\
            .filter(RecommendationEvent.user_id == user_id, RecommendationEvent.session_id == session_id)\
            .order_by(RecommendationEvent.created_at.desc())\
            .limit(5).all()
        recent_ids = [e.dish_id for e in recent_events]

        # 3. Candidate Generation
        # Hard constraints: Open restaurants, price range, dietary tags, availability
        query = self.db.query(Dish).join(Restaurant).filter(
            Restaurant.is_open == True,
            Dish.is_available == True,
            Dish.price >= b_min,
            Dish.price <= b_max,
            Dish.id.notin_(recent_ids)
        )

        if dietary_flags:
            for flag in dietary_flags:
                query = query.filter(Dish.dietary_tags.contains([flag]))
        
        if exclude_cuisines:
            query = query.filter(Dish.cuisine.notin_(exclude_cuisines))

        candidates = query.all()

        if not candidates:
            return None

        # 4. Check for Cold Start
        order_count = self.db.query(Order).filter(Order.user_id == user_id).count()
        is_cold_start = order_count < 3

        if is_cold_start:
            # Fallback to city-level trending (simplified: highest rated)
            candidates.sort(key=lambda x: x.rating or 0, reverse=True)
            return random.choice(candidates[:10]) # Pick from top 10

        # 5. Weight Assignment (60% Fav, 30% Similar, 10% Novel)
        fav_cuisines = prefs.favourite_cuisines if prefs else []
        
        # For simulation, let's assume "Similar" means cuisines that share the same first 3 letters 
        # (in a real app this would be a similarity matrix)
        
        weighted_candidates = []
        weights = []

        for dish in candidates:
            tier = "novel"
            weight = 1 # 10% base
            
            if dish.cuisine in fav_cuisines:
                tier = "favourite"
                weight = 6 # 60%
            else:
                # Check for similarity (simple heuristic for demo)
                is_similar = any(dish.cuisine[:3].lower() == fav[:3].lower() for fav in fav_cuisines)
                if is_similar:
                    tier = "similar"
                    weight = 3 # 30%
            
            weighted_candidates.append((dish, tier))
            weights.append(weight)

        # 6. Stochastic Selection
        selected_dish, tier = random.choices(weighted_candidates, weights=weights, k=1)[0]
        
        # Attach tier info for response
        selected_dish.selected_tier = tier
        return selected_dish
