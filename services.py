from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from passlib.context import CryptContext
from typing import Annotated
from jose import jwt, JWTError
import os

from dtos import UserRequest, TransportModel
from models import User, FindUser, Transport, Rent, FindRent, FindTransport

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE = os.getenv("ACCESS_TOKEN_EXPIRE")

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth_bearer = OAuth2PasswordBearer(tokenUrl='api/Account/SignIn')

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)
    
def create_user_request(data: UserRequest, db: Session):
    bcrypt_password = bcrypt_context.hash(data.password)
    user = User(name=data.name, password=bcrypt_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(user: User, data: UserRequest, db: Session):
    user.name = data.name
    bcrypt_password = bcrypt_context.hash(data.password)
    user.password = bcrypt_password
    db.add(user)
    db.commit()
    db.refresh(user)
    return data

def authenticate_user(name: str, password: str, db: Session):    
    user = FindUser.get_user_by_name(name, db)
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"})
    return user

def create_access_token(user: User):
    encode = {'id': user.id}
    expires = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE))
    encode.update({"exp": expires})
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

async def get_current_user(token: Annotated[str, Depends(oauth_bearer)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get('id')
        if id is None:
            raise credentials_exception
        return id
    except JWTError:
        raise credentials_exception

"""
space
"""

VALID_TRANSPORT_TYPES = ['Car', 'Bike', 'Scooter']

def create_transport_request(data: TransportModel, db: Session, user_id: int):
    transport_type = data.transportType
    if transport_type in VALID_TRANSPORT_TYPES:
        transport = Transport(user_id=user_id, canBeRented=data.canBeRented, transportType=transport_type, model=data.model, color=data.color, identifier=data.identifier, description=data.description, latitude=data.latitude, longitude=data.longitude, minutePrice=data.minutePrice, dayPrice=data.dayPrice)
        db.add(transport)
        db.commit()
        db.refresh(transport)
        return transport
    else:
        raise HTTPException(status_code=400, detail="Invalid transport type")

def update_transport(transport: Transport, data: TransportModel, db: Session):
    transport_type = data.transportType
    if transport_type in VALID_TRANSPORT_TYPES:
        transport.canBeRented=data.canBeRented
        transport.transportType=transport_type,
        transport.model=data.model
        transport.color=data.color
        transport.identifier=data.identifier
        transport.description=data.description
        transport.latitude=data.latitude
        transport.longitude=data.longitude
        transport.minutePrice=data.minutePrice
        transport.dayPrice=data.dayPrice
        db.add(transport)
        db.commit()
        db.refresh(transport)
        return transport
    else:
        raise HTTPException(status_code=400, detail="Invalid transport type")
    
def delete_transport(transport: Transport, db: Session):
    data = db.query(Transport).filter(Transport.id == transport.id).delete()
    db.commit()
    return data

def is_renter(user: User, rent: Rent):
    return user.id == rent.renter_user_id

def is_owner(user: User, transport_id: int, db: Session):
    transport = FindTransport.get_transport_by_id(transport_id, db)
    return transport and user.id == transport.user_id

def find_rent(rentId: int, user: User, db: Session):
    rent = FindRent.get_rent_by_id(rentId, db)

    if not rent:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    if not (is_renter(user, rent) or is_owner(user, rent.transportId, db)):
        raise HTTPException(status_code=403, detail="You do not have permission to view this rental")
    
    return rent

def create_rent_request(transportId: int, rentType: str, duration: int, user: User, db: Session):
    transport = FindTransport.get_transport_by_id(transportId, db)

    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    
    if not transport.canBeRented:
        raise HTTPException(status_code=404, detail="Transport is rented")
    
    if is_owner(user, transportId, db):
        raise HTTPException(status_code=400, detail="You cannot rent your own transport")
    
    time = datetime.now()
    rent = Rent(rentType=rentType, transportId=transportId, renter_user_id=user.id)
    
    rent.startTime = time.strftime("%Y-%m-%d %H:%M:%S")
    if rentType == 'Minutes':
        rent.endTime = (time + timedelta(minutes=duration)).strftime("%Y-%m-%d %H:%M:%S")
    elif rentType == 'Days':
        rent.endTime = (time + timedelta(days=duration)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        raise HTTPException(status_code=400, detail="Invalid rent type")
    
    db.add(rent)
    db.add(transport)
    db.commit()
    db.refresh(rent)
    db.refresh(transport)
    return rent
    