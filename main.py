import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from database import engine, Base
from routers.user import account
from routers.transport import transport
from routers.rent import rent

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/main")
def main():
    return PlainTextResponse("Главная страница")

app.include_router(account)
app.include_router(transport)
app.include_router(rent)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run('main:app', host='0.0.0.0', port=3000, reload=False)