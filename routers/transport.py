from fastapi import APIRouter, Depends, HTTPException

from models import Transport, FindTransport, User
from dtos import TransportModel
from database import db_dependency
from services import create_transport_request, update_transport, delete_transport
from routers.user import user_с

transport = APIRouter(prefix='/api/Transport', tags=["TransportController"])

@transport.get("/{id}", response_model=TransportModel)
async def get_transport(id: int, db: db_dependency):
    transport = FindTransport.get_transport_by_id(id, db)
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    return transport

@transport.post("/", response_model=TransportModel)
async def create_user_transport(data: TransportModel, db: db_dependency, user: user_с):
    transport = create_transport_request(data, db, user.id)
    return transport

def is_owner(user: User, transport: Transport) -> bool:
    return user.id == transport.user_id

@transport.put("/{id}", response_model=TransportModel)
async def update_user_transport(id: int, data: TransportModel, db: db_dependency, user: user_с):
    transport = FindTransport.get_transport_by_id(id, db)
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    
    if not is_owner(user, transport):
        raise HTTPException(status_code=403, detail="У вас нет разрешения на изменение этого транспорта")
    
    return update_transport(transport, data, db)

@transport.delete("/{id}")
async def update_user_transport(id: int, db: db_dependency, user: user_с):
    transport = FindTransport.get_transport_by_id(id, db)
    
    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    
    if not is_owner(user, transport):
        raise HTTPException(status_code=403, detail="У вас нет разрешения на изменение этого транспорта")
    
    return delete_transport(transport, db)
