from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    transports = relationship("Transport", back_populates="user")
    rents_as_renter = relationship("Rent", back_populates="renter_user", foreign_keys="Rent.renter_user_id")
    name = Column(String, unique=True, index=True)
    password = Column(String)
    disabled = Column(Boolean, default=False)
    balance = Column(Float, default=0)
    isAdmin = Column(Boolean, default=False)

class FindUser:
    @staticmethod
    def get_user_by_id(id: int, db: Session):
        return db.query(User).filter(User.id == id).first()

    @staticmethod
    def get_user_by_name(name: str, db: Session):
        return db.query(User).filter(User.name == name).first()

class Transport(Base):
    __tablename__ = 'transport'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="transports")
    canBeRented = Column(Boolean, default=True)
    rents = relationship("Rent", back_populates="transport")
    transportType = Column(String)
    model = Column(String)
    color = Column(String)
    identifier = Column(String, unique=True)
    description = Column(String, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    minutePrice = Column(Float, nullable=True)
    dayPrice = Column(Float, nullable=True)

class FindTransport:
    @staticmethod
    def get_transport_by_id(id: int, db: Session):
        return db.query(Transport).filter(Transport.id == id).first()

class Rent(Base):
    __tablename__ = 'rent'
    
    id = Column(Integer, primary_key=True, index=True)
    rentType = Column(String)
    transportId = Column(Integer, ForeignKey('transport.id'))
    transport = relationship("Transport", back_populates="rents")
    renter_user_id = Column(Integer, ForeignKey('users.id'))
    renter_user = relationship("User", back_populates="rents_as_renter", foreign_keys=[renter_user_id])
    startTime = Column(String)
    endTime = Column(String, nullable=True)
    priceOfUnit = Column(Float)
    finalPrice = Column(Float, nullable=True)

class FindRent:
    @staticmethod
    def get_rent_by_id(id: int, db: Session):
        return db.query(Rent).filter(Rent.id == id).first()
    
    @staticmethod
    def get_rent_by_user_id(id: int, db: Session):
        return db.query(Rent).filter(Rent.renter_user_id == id).all()
    
    @staticmethod
    def get_rent_by_transport_id(id: int, db: Session):
        return db.query(Rent).filter(Rent.transportId == id).all()
    
    @staticmethod
    def get_rent_by_transport_id_and_user_id(transportId: int, user_id: int, db: Session):
        return db.query(Rent).join(Transport, Rent.transportId == Transport.id).filter(
        Rent.transportId == transportId,
        Transport.user_id == user_id
    ).all()