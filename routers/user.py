from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse

from dtos import UserRequest, Token
from models import User, FindUser
from database import db_dependency
from services import get_current_user, update_user, create_user_request, authenticate_user, create_access_token

account = APIRouter(prefix='/api/Account', tags=["AccountController"])
user_dependency = Annotated[User, Depends(get_current_user)]

async def get_current_active_user(current_user: user_dependency, db: db_dependency):
    user = FindUser.get_user_by_id(current_user, db)

    if user.disabled:
        raise HTTPException(status_code=403, detail="Inactive user")
    
    return user

async def admin_endpoint(current_user: user_dependency, db: db_dependency):
    user = FindUser.get_user_by_id(current_user, db)

    if not user.isAdmin:
        raise HTTPException(status_code=403, detail="You do not have permission")
    
    return user

user_с = Annotated[User, Depends(get_current_active_user)]
user_a = Annotated[User, Depends(admin_endpoint)]

@account.post('/SignUp', response_model=Token)
async def create_user(data: UserRequest, db: db_dependency):
    user = create_user_request(data, db)
    token = create_access_token(user)
    return Token(access_token=token, token_type='bearer')

@account.post('/SignIn', response_model=Token)
async def login_for_access_token(data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(data.username, data.password, db)
    token = create_access_token(user)
    return Token(access_token=token, token_type='bearer')

@account.get('/Me')
async def get_current_account(user: user_с):
    return user

@account.put('/Update')
async def update_current_account(user: user_с, data: UserRequest, db: db_dependency): 
    return update_user(user, data, db)

@account.post('/SignOut')
async def logout(user: user_dependency):
    RedirectResponse(url="/main")
    return user