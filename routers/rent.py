from fastapi import APIRouter
from sqlalchemy import func

from database import db_dependency
from routers.user import user_с
from models import Transport
from services import find_rent, create_rent_request, user_rent_history, transport_rent_history, end_rent
from dtos import RentModel

rent = APIRouter(prefix='/api/Rent', tags=["RentController"])

@rent.get("/Transport", summary="Получить доступные транспортные средства для аренды")
async def get_available_rent(
    latitude: float = None,
    longitude: float = None,
    radius: float = None,
    type: str = None,
    db: db_dependency = None):
    query = db.query(Transport).filter(Transport.canBeRented == True)

    if latitude is not None and longitude is not None and radius is not None:
        query = query.filter(
            func.power(Transport.latitude - latitude, 2) + func.power(Transport.longitude - longitude, 2) <= func.power(radius, 2))
        
    if type is not None:
        query = query.filter(Transport.transportType == type)

    available_transport = query.all()
    return available_transport

@rent.get("/{rentId}", summary="Получить информацию о аренде по ID")
async def get_rent(rentId: int, user: user_с, db: db_dependency):
    rent = find_rent(rentId, user, db)
    return rent

@rent.post("/New/{transportId}", summary="Создать новую аренду")
async def create_rent(data: RentModel, user: user_с, db: db_dependency):
    rent = create_rent_request(data, user, db)
    return rent

@rent.get("/MyHistory/", summary="Получить историю аренд текущего пользователя")
async def my_rent(user: user_с, db: db_dependency):
    rent = user_rent_history(user, db)
    return rent

@rent.get("/TransportHistory/{transportId}", summary="Получить историю аренды транспорта текущего пользователя")
async def my_transport_rent(transportId: int, user: user_с, db: db_dependency):
    rent = transport_rent_history(transportId, user, db)
    return rent

@rent.post("/End/{rentId}", summary="Завершить аренду по ID")
async def end_my_rent(rentId: int, latitude: float, longitude: float, user: user_с, db: db_dependency):
    rent = end_rent(rentId, latitude, longitude, user, db)
    return rent



