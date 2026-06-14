import os
import sys
import pandas as pd
import numpy as np
import joblib

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from backend.database import engine, Base, SessionLocal
from backend.models import Car

from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

CSV_PATH = os.path.join(project_root, "data", "cars-dataset-main", "vehicle_data_sample.csv")
MODEL_PRICE_PATH = os.path.join(project_root, "models", "price_model.pkl")
MODEL_PERF_PATH = os.path.join(project_root, "models", "performance_model.pkl")

def ingest_data_and_train():
    print(f"Loading data from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    
    # Select and rename required columns to match DB schema
    column_mapping = {
        'brand': 'company_name',
        'model': 'car_name',
        'engine_type': 'engine_type',
        'fuel_type': 'fuel_type',
        'seats': 'seats',
        'cubic_capacity_cc': 'cc_capacity',
        'power_hp': 'horsepower',
        'top_speed_kmh': 'total_speed',
        'acceleration_0_100_s': 'performance_0_100',
        'price_eur': 'price',
        'torque_nm': 'torque'
    }
    
    # Keep only columns that exist
    cols_to_keep = [col for col in column_mapping.keys() if col in df.columns]
    df = df[cols_to_keep].rename(columns=column_mapping)
    
    # Drop rows without critical info for database insertion
    df_db = df.dropna(subset=['company_name', 'car_name', 'price', 'performance_0_100'])
    
    # Recreate the database table
    print("Recreating database table...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Insert data into database
    print("Inserting data into database...")
    db = SessionLocal()
    for _, row in df_db.iterrows():
        car = Car(
            company_name=str(row['company_name']),
            car_name=str(row['car_name']),
            engine_type=str(row['engine_type']) if not pd.isna(row.get('engine_type')) else None,
            fuel_type=str(row['fuel_type']) if not pd.isna(row.get('fuel_type')) else None,
            seats=int(row['seats']) if not pd.isna(row.get('seats')) else None,
            cc_capacity=float(row['cc_capacity']) if not pd.isna(row.get('cc_capacity')) else None,
            horsepower=float(row['horsepower']) if not pd.isna(row.get('horsepower')) else None,
            total_speed=float(row['total_speed']) if not pd.isna(row.get('total_speed')) else None,
            performance_0_100=float(row['performance_0_100']),
            price=float(row['price']) * 90.0,
            torque=float(row['torque']) if not pd.isna(row.get('torque')) else None
        )
        db.add(car)
    db.commit()
    db.close()
    
    # Prepare data for Machine Learning: drop rows without cc_capacity or engine_type
    print("Preparing models for training...")
    df_ml = df.dropna(subset=['cc_capacity', 'engine_type']).copy()
    df_ml['price'] = df_ml['price'] * 90.0
    
    X = df_ml[['cc_capacity', 'engine_type']].copy()
    
    # Handle price with log transformation, as expected by the frontend logic
    y_price = np.log1p(df_ml['price'])
    y_perf = df_ml['performance_0_100']
    
    # Setup preprocessing pipeline: 
    # - Pass through numeric cc_capacity (with imputation if needed)
    # - OneHotEncode categorical engine_type
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', SimpleImputer(strategy='median'), ['cc_capacity']),
            ('cat', Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
                ('onehot', OneHotEncoder(handle_unknown='ignore'))
            ]), ['engine_type'])
        ])
    
    # Price Model Pipeline
    price_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    # Performance Model Pipeline
    perf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    # Train
    print("Training Price Model...")
    price_pipeline.fit(X, y_price)
    
    print("Training Performance Model...")
    perf_pipeline.fit(X, y_perf)
    
    # Ensure models directory exists
    os.makedirs(os.path.dirname(MODEL_PRICE_PATH), exist_ok=True)
    
    print("Saving models...")
    joblib.dump(price_pipeline, MODEL_PRICE_PATH)
    joblib.dump(perf_pipeline, MODEL_PERF_PATH)
    
    print("Data ingestion and training complete!")
    
    # Small test
    test_features = pd.DataFrame([{'cc_capacity': 2000.0, 'engine_type': 'Inline 4-cylinder naturally aspirated gasoline'}])
    pred_price = np.expm1(price_pipeline.predict(test_features)[0])
    pred_perf = perf_pipeline.predict(test_features)[0]
    print(f"Sample prediction for 2000cc Inline 4:")
    print(f"Predicted Price: {pred_price:.2f}")
    print(f"Predicted Performance 0-100: {pred_perf:.2f}")

if __name__ == "__main__":
    ingest_data_and_train()
