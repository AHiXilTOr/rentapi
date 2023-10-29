import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from database import engine, Base
from routers.user import account
from routers.transport import transport
from routers.rent import rent
from routers.payment import payment
from routers.admin import adminaccount, admintranstor, adminrent
from admin import initialize_admin

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/main")
def main():
    return PlainTextResponse("Главная страница")

routers = [account, transport, rent, payment, adminaccount, admintranstor, adminrent]
for router in routers:
    app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    initialize_admin()

if __name__ == "__main__":
    uvicorn.run('main:app', host='0.0.0.0', port=3000, reload=False)