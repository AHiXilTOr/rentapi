from fastapi import APIRouter

from database import db_dependency
from routers.user import user_с, user_a
from models import FindUser

payment = APIRouter(prefix='/api/Payment', tags=["PaymentController"])

@payment.post("/Hesoyam", summary="Увеличить баланс текущего пользователя на 250000")
async def hesoyam(user: user_с, db: db_dependency):
    user.balance += 250000
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@payment.post("/Hesoyam/{accountId}", summary="Увеличить баланс пользователя по ID на 250000")
async def hesoyam(user: user_a, db: db_dependency, accountId: float):
    user = FindUser.get_user_by_id(accountId, db)
    user.balance += 250000
    db.add(user)
    db.commit()
    db.refresh(user)
    return user