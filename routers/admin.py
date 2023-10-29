from fastapi import APIRouter, HTTPException

from database import db_dependency
from routers.user import user_a
from models import User, FindUser, Transport, FindTransport, FindRent
from dtos import AdminUserRequest, AdminTransportModel, AdminRentModel, AdminRentModelWithAll
from services import create_user_request, update_user, create_transport_request, update_transport, create_rent_request, end_rent

adminaccount = APIRouter(prefix='/api/Admin/Account', tags=["AdminAccountController"])

@adminaccount.get("/")
async def get_all_accounts(user: user_a, db: db_dependency, start: int = 0, count: int = 10):
    accounts = db.query(User).offset(start).limit(count).all()
    return accounts

@adminaccount.get("/{id}")
async def get_account_by_id(id: int, user: user_a, db: db_dependency):
    account = FindUser.get_user_by_id(id, db)
    return account

@adminaccount.post("/")
async def create_account(data: AdminUserRequest, user: user_a, db: db_dependency):
    account = create_user_request(data, db)
    return account

@adminaccount.put("/{id}")
async def update_account(id: int, data: AdminUserRequest, user: user_a, db: db_dependency):
    user = FindUser.get_user_by_id(id, db)
    account = update_user(user, data, db)
    return account

@adminaccount.delete("/{id}")
async def delete_account(id: int, user: user_a, db: db_dependency):
    user = FindUser.get_user_by_id(id, db)

    if user is None:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(user)
    db.commit()
    return user

admintranstor = APIRouter(prefix='/api/Admin/Transport', tags=["AdminTranstorController"])

@admintranstor.get("/")
async def get_all_transport(user: user_a, db: db_dependency, start: int = 0, count: int = 10, transportType: str = 'All'):
    query = db.query(Transport)
    
    if transportType != "All":
        query = query.filter(Transport.transportType == transportType)
    
    query = query.offset(start).limit(count)
    transports = query.all()
    return transports

@admintranstor.get("/{id}")
async def get_transport_by_id(id: int, user: user_a, db: db_dependency):
    transport = FindTransport.get_transport_by_id(id, db)
    return transport

@admintranstor.post("/")
async def create_transport(data: AdminTransportModel, user: user_a, db: db_dependency):
    transport = create_transport_request(data, db)
    return transport

@admintranstor.put("/{id}")
async def update_transport_by_id(id: int, data: AdminTransportModel, user: user_a, db: db_dependency):
    query = FindTransport.get_transport_by_id(id, db)
    transport = update_transport(query, data, db)
    return transport

@admintranstor.delete("/{id}")
async def delete_transport(id: int, user: user_a, db: db_dependency):
    transport = FindTransport.get_transport_by_id(id, db)

    if transport is None:
        raise HTTPException(status_code=404, detail="Transport not found")

    db.delete(transport)
    db.commit()
    return transport

adminrent = APIRouter(prefix='/api/Admin', tags=["AdminRentController"])

@adminrent.get("/Rent/{rentId}")
async def get_rent_by_id(rentId: int, user: user_a, db: db_dependency):
    rent = FindRent.get_rent_by_id(rentId, db)
    return rent

@adminrent.get("/UserHistory/{userId}")
async def get_rent_history_by_account_id(userId: int, user: user_a, db: db_dependency):
    rent = FindRent.get_rent_by_user_id(userId, db)
    return rent

@adminrent.get("/TransportHistory/{transportId}")
async def get_rent_transport_history_by_account_id(transportId: int, user: user_a, db: db_dependency):
    rent = FindRent.get_rent_by_transport_id(transportId, db)
    return rent

@adminrent.post("/Rent")
async def create_rent_by_account_id(data: AdminRentModel, user: user_a, db: db_dependency):
    rent = create_rent_request(data, user, db)
    return rent

@adminrent.post("/Rent/End/{rentId}")
async def end_rent_by_account_id(rentId: int, latitude: float, longitude: float, user: user_a, db: db_dependency):
    rent = end_rent(rentId, latitude, longitude, user, db)
    return rent

VALID_RENT_TYPES = ['Minutes', 'Days']

@adminrent.put("/Rent/{rentId}")
async def update_rent_by_account_id(rentId: int, data: AdminRentModelWithAll, user: user_a, db: db_dependency):
    try:
        if not data.rentType in VALID_RENT_TYPES:
            raise HTTPException(status_code=400, detail="Invalid rent type")
        rent = FindRent.get_rent_by_id(rentId, db)
        rent.rentType=data.rentType
        rent.transportId=data.transportId
        rent.renter_user_id=data.renter_user_id
        rent.startTime=data.startTime
        rent.endTime=data.endTime
        rent.priceOfUnit=data.priceOfUnit
        rent.finalPrice=data.finalPrice
        db.add(rent)
        db.commit()
        db.refresh(rent)
        return rent
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'{e}')

@adminrent.delete("/Rent/End/{rentId}")
async def delete_rent_by_account_id(rentId: int, user: user_a, db: db_dependency):
    rent = FindRent.get_rent_by_id(rentId, db)

    if rent is None:
        raise HTTPException(status_code=404, detail="Rental not found")

    db.delete(rent)
    db.commit()
    return rent