from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import joblib
import os
import numpy as np
from pydantic import BaseModel

from . import models, database

app = FastAPI(title="Car Evolution System API")

# Setup CORS for the React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
model_perf_path = os.path.join(project_root, "models", "performance_model.pkl")
model_price_path = os.path.join(project_root, "models", "price_model.pkl")

class SearchRequest(BaseModel):
    company_name: str
    model_name: str
    year: int
    color: str
    seats: int
    cc_capacity: float

@app.get("/")
def read_root():
    return {"message": "Welcome to the Car Evolution System API!"}

@app.get("/api/cars")
def get_cars(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    cars = db.query(models.Car).offset(skip).limit(limit).all()
    return cars

@app.get("/api/cars/stats")
def get_car_stats(db: Session = Depends(database.get_db)):
    # Very simple aggregate logic for charts
    total_cars = db.query(models.Car).count()
    return {"total_cars": total_cars}

@app.get("/api/engine_types")
def get_engine_types(db: Session = Depends(database.get_db)):
    results = db.query(models.Car.engine_type).distinct().filter(
        models.Car.engine_type != None,
        models.Car.engine_type != ""
    ).order_by(models.Car.engine_type).all()
    return [r[0] for r in results]

@app.post("/api/search_car")
def search_car(req: SearchRequest, db: Session = Depends(database.get_db)):
    query = db.query(models.Car)
    
    # Filter by company_name if provided
    if req.company_name.strip():
        comp_term = f"%{req.company_name.strip()}%"
        query = query.filter(models.Car.company_name.like(comp_term))
        
    # Filter by model_name if provided
    if req.model_name.strip():
        model_term = f"%{req.model_name.strip()}%"
        query = query.filter(
            (models.Car.company_name.like(model_term)) | 
            (models.Car.car_name.like(model_term))
        )
        
    # Filter by seats if provided
    if req.seats:
        query = query.filter(models.Car.seats == req.seats)
        
    candidates = query.all()
    
    # Fallbacks if strict filtering yields no results
    # 1. Try matching company and model names (relaxed seats)
    if not candidates and (req.company_name.strip() or req.model_name.strip()):
        query2 = db.query(models.Car)
        if req.company_name.strip():
            query2 = query2.filter(models.Car.company_name.like(f"%{req.company_name.strip()}%"))
        if req.model_name.strip():
            query2 = query2.filter(
                (models.Car.company_name.like(f"%{req.model_name.strip()}%")) |
                (models.Car.car_name.like(f"%{req.model_name.strip()}%"))
            )
        candidates = query2.all()
        
    # 2. Try matching just model name
    if not candidates and req.model_name.strip():
        candidates = db.query(models.Car).filter(
            (models.Car.company_name.like(f"%{req.model_name.strip()}%")) |
            (models.Car.car_name.like(f"%{req.model_name.strip()}%"))
        ).all()
        
    # 3. Try matching just company name
    if not candidates and req.company_name.strip():
        candidates = db.query(models.Car).filter(
            models.Car.company_name.like(f"%{req.company_name.strip()}%")
        ).all()
        
    # 4. Fallback to all cars
    if not candidates:
        candidates = db.query(models.Car).all()
        
    # Find closest match by cc_capacity
    closest_car = None
    if candidates:
        closest_car = min(candidates, key=lambda c: abs((c.cc_capacity or 0) - req.cc_capacity))
        
    if not closest_car:
        raise HTTPException(status_code=404, detail="No matching cars found in database.")
        
    # Run prediction model on the input CC and closest car's engine_type
    predicted_price = closest_car.price
    predicted_perf = closest_car.performance_0_100
    
    if os.path.exists(model_perf_path) and os.path.exists(model_price_path):
        try:
            ml_model_perf = joblib.load(model_perf_path)
            ml_model_price = joblib.load(model_price_path)
            
            import pandas as pd
            import numpy as np
            features = pd.DataFrame([{
                'cc_capacity': req.cc_capacity,
                'engine_type': closest_car.engine_type or "I4"
            }])
            
            pred_perf = ml_model_perf.predict(features)[0]
            pred_price = ml_model_price.predict(features)[0]
            
            # Apply expm1 to reverse the log transformation of the price model
            predicted_price = round(float(np.expm1(pred_price)), 2)
            predicted_perf = round(float(pred_perf), 2)
        except Exception as e:
            print(f"Prediction fallback error: {e}")
            
    return {
        "matched_company_name": closest_car.company_name,
        "matched_car_name": closest_car.car_name,
        "matched_price": closest_car.price,
        "matched_cc": closest_car.cc_capacity,
        "matched_seats": closest_car.seats,
        "predicted_price": predicted_price,
        "predicted_performance_0_100": predicted_perf
    }

@app.post("/api/predict_performance")
def predict_performance(req: SearchRequest, db: Session = Depends(database.get_db)):
    # Forward to search_car for backward compatibility
    return search_car(req, db)
