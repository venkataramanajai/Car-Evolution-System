from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    car_name = Column(String, index=True)
    engine_type = Column(String)
    fuel_type = Column(String)
    seats = Column(Integer)
    cc_capacity = Column(Float)
    horsepower = Column(Float)
    total_speed = Column(Float)
    performance_0_100 = Column(Float)
    price = Column(Float)
    torque = Column(Float)
