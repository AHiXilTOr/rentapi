from pydantic import BaseModel

class UserRequest(BaseModel):
    name: str
    password: str

class AdminUserRequest(UserRequest):
    isAdmin: bool
    balance: float

class Token(BaseModel):
    access_token: str
    token_type: str

class TransportModel(BaseModel):
    canBeRented: bool
    transportType: str = "Car"
    model: str = "Some Model"
    color: str = "White"
    identifier: str = "ABC123"
    description: str = ""
    latitude: float
    longitude: float
    minutePrice: float
    dayPrice: float

class AdminTransportModel(TransportModel):
    ownerId: int

class RentModel(BaseModel):
    rentType: str
    transportId: int
    duration: int

class AdminRentModel(RentModel):
    renter_user_id: int

class AdminRentModelWithAll(AdminRentModel):
    startTime: str
    endTime: str
    priceOfUnit: float
    finalPrice: float