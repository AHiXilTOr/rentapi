from pydantic import BaseModel
from typing import Optional
from enum import Enum

class UserRequest(BaseModel):
    name: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TransportType(Enum):
    Car = 'Car'
    Bike = 'Bike'
    Scooter = 'Scooter'

class TransportModel(BaseModel):
    canBeRented: bool
    transportType: str
    model: str
    color: str
    identifier: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    minutePrice: Optional[float] = None
    dayPrice: Optional[float] = None