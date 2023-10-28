from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from database import Base

# AccountController
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    transports = relationship("Transport", back_populates="user")
    rents_as_renter = relationship("Rent", back_populates="renter_user", foreign_keys="Rent.renter_user_id")
    name = Column(String, unique=True, index=True)
    password = Column(String)
    disabled = Column(Boolean, default=False)
    users_history = relationship("RentHistory", back_populates="renter_user", foreign_keys="RentHistory.renter_user_id")

class FindUser:
    @staticmethod
    def get_user_by_id(id: int, db: Session):
        return db.query(User).filter(User.id == id).first()

    @staticmethod
    def get_user_by_name(name: str, db: Session):
        return db.query(User).filter(User.name == name).first()

# TransportController
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

# RentController
class Rent(Base):
    __tablename__ = 'rent'
    
    id = Column(Integer, primary_key=True, index=True)
    rentType = Column(String)
    transportId = Column(Integer, ForeignKey('transport.id'))
    transport = relationship("Transport", back_populates="rents")
    renter_user_id = Column(Integer, ForeignKey('users.id'))
    renter_user = relationship("User", back_populates="rents_as_renter", foreign_keys=[renter_user_id])
    startTime = Column(String)
    endTime = Column(String)

    # широта и долгота сразу переходят в модель транспорта, а при ручном завершении endTime изменяется

class FindRent:
    @staticmethod
    def get_rent_by_id(id: int, db: Session):
        return db.query(Rent).filter(Rent.id == id).first()

class RentHistory(Base):
    __tablename__ = 'rent_history'
    
    id = Column(Integer, primary_key=True, index=True)
    renter_user_id = Column(Integer, ForeignKey('users.id'))
    renter_user = relationship("User", back_populates="rents_history")
    startTime = Column(String)
    endTime = Column(String)
    startLatitude = Column(Float)
    startLongitude = Column(Float)
    endLatitude = Column(Float)
    endLongitude = Column(Float)

# @staticmethod
#     def get_transport_rent_history_by_id(transport_id: int, db: Session):
#         return db.query(RentHistory).join(Rent, Rent.id == RentHistory.rent_id).filter(Rent.transportId == transport_id).all()

    # def get_user_rent_history_by_id(user_id: int, db: Session):
    #     return db.query(RentHistory).filter(RentHistory.renter_user_id == user_id).all()