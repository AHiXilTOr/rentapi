from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from passlib.context import CryptContext
from typing import Annotated
from jose import jwt, JWTError
from sqlalchemy.exc import *
import os

from models import User, FindUser, Transport, Rent, FindRent, FindTransport

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE = os.getenv("ACCESS_TOKEN_EXPIRE")

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth_bearer = OAuth2PasswordBearer(tokenUrl='api/Account/SignIn')

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)
    
def hash(password):
    password = bcrypt_context.hash(password)
    return password

def create_user_request(data, db: Session):
    bcrypt_password = hash(data.password)
    user = User(name=data.name, password=bcrypt_password)

    if hasattr(data, 'isAdmin'):
        user.isAdmin = data.isAdmin

    if hasattr(data, 'balance'):
        user.balance = data.balance

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(user: User, data, db: Session):
    user.name = data.name
    bcrypt_password = bcrypt_context.hash(data.password)
    user.password = bcrypt_password

    if hasattr(data, 'isAdmin'):
        user.isAdmin = data.isAdmin

    if hasattr(data, 'balance'):
        user.balance = data.balance

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

VALID_TRANSPORT_TYPES = ['Car', 'Bike', 'Scooter']

def create_transport_request(data, db: Session, user_id: int = 0):
    try:
        transport_type = data.transportType
        
        if not transport_type in VALID_TRANSPORT_TYPES:
            raise HTTPException(status_code=400, detail="Invalid transport type")
        
        transport = Transport(user_id=user_id, canBeRented=data.canBeRented, transportType=transport_type, model=data.model, color=data.color, identifier=data.identifier, description=data.description, latitude=data.latitude, longitude=data.longitude, minutePrice=data.minutePrice, dayPrice=data.dayPrice)
        
        if hasattr(data, 'ownerId'):
            transport.user_id = data.ownerId

        db.add(transport)
        db.commit()
        db.refresh(transport)
        return transport
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    
def update_transport(transport: Transport, data, db: Session):
    try:
        transport_type = data.transportType

        if not transport_type in VALID_TRANSPORT_TYPES:
            raise HTTPException(status_code=400, detail="Invalid transport type")
        
        if hasattr(data, 'ownerId'):
            transport.user_id = data.ownerId

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
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    
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

def create_rent_request(data, user: User, db: Session):
    transport = FindTransport.get_transport_by_id(data.transportId, db)

    if not transport:
        raise HTTPException(status_code=404, detail="Transport not found")
    
    if not transport.canBeRented:
        raise HTTPException(status_code=404, detail="Transport is rented")
    
    time = datetime.now()
    rent = Rent(rentType=data.rentType, transportId=data.transportId)

    if hasattr(data, "renter_user_id"):
        rent.renter_user_id=data.renter_user_id
    else:
        if is_owner(user, data.transportId, db):
            raise HTTPException(status_code=400, detail="You cannot rent your own transport")
        rent.renter_user_id=user.id
    
    rent.startTime = time.strftime("%Y-%m-%d %H:%M:%S")
    
    if data.rentType == 'Minutes':
        rent.endTime = (time + timedelta(minutes=data.duration)).strftime("%Y-%m-%d %H:%M:%S")
        rent.priceOfUnit = transport.minutePrice
        rent.finalPrice = transport.minutePrice * data.duration
    elif data.rentType == 'Days':
        rent.endTime = (time + timedelta(days=data.duration)).strftime("%Y-%m-%d %H:%M:%S")
        rent.priceOfUnit = transport.dayPrice
        rent.finalPrice = transport.dayPrice * data.duration * 84
    else:
        raise HTTPException(status_code=400, detail="Invalid rent type")
    
    transport.canBeRented = False

    db.add(rent)
    db.add(transport)
    db.commit()
    db.refresh(rent)
    db.refresh(transport)
    return rent
    
def user_rent_history(user: User, db: Session):
    rent = FindRent.get_rent_by_user_id(user.id, db)
    return rent

def transport_rent_history(transportId: int, user: User, db: Session):
    rent = FindRent.get_rent_by_transport_id_and_user_id(transportId, user.id, db)

    if not rent:
        raise HTTPException(status_code=400, detail="You cannot see someone else car")

    return rent

def end_rent(rentId: int, latitude: float, longitude: float, user: User, db: Session):
    rent = FindRent.get_rent_by_id(rentId, db)

    if not rent:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    if not user.isAdmin:
        if not rent.renter_user_id == user.id:
            raise HTTPException(status_code=403, detail="You do not have permission")
    
    time = datetime.now()

    if time > datetime.strptime(rent.endTime, "%Y-%m-%d %H:%M:%S"):
        raise HTTPException(status_code=400, detail="Rental has already ended")
    
    rent.endTime = time.strftime("%Y-%m-%d %H:%M:%S")

    transport = FindTransport.get_transport_by_id(rent.transportId, db)
    transport.latitude = latitude
    transport.longitude = longitude
    transport.canBeRented = True
    db.add(rent)
    db.add(transport)
    db.commit()
    db.refresh(rent)
    db.refresh(transport)
    return rent