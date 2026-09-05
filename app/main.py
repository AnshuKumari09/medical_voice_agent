from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.database import Base, engine


app = FastAPI(
    title="MediReach Voice Assistant",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_database_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables checked/created")


app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "message": "MediReach Voice Assistant API is running",
    }
