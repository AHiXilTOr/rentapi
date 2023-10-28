from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func

from database import db_dependency
from routers.user import user_с
from models import Transport, FindTransport
from services import find_rent, create_rent_request

rent = APIRouter(prefix='/api/Rent', tags=["RentController"])

@rent.get("/Transport")
async def get_available_rent(
    lat: float = None,
    long: float = None,
    radius: float = None,
    type: str = None,
    db: db_dependency = None):
    query = db.query(Transport).filter(Transport.canBeRented == True)

    if lat is not None and long is not None and radius is not None:
        query = query.filter(
            func.power(Transport.latitude - lat, 2) + func.power(Transport.longitude - long, 2) <= func.power(radius, 2))
        
    if type is not None:
        query = query.filter(Transport.transportType == type)

    available_transport = query.all()
    return available_transport

@rent.get("/{rentId}")
async def get_rent(rentId: int, user: user_с, db: db_dependency):
    rent = find_rent(rentId, user, db)
    return rent

@rent.post("/New/{transportId}")
async def create_rent(transportId: int, rentType: str, duration: int, user: user_с, db: db_dependency):
    rent = create_rent_request(transportId, rentType, duration, user, db)
    return rent





