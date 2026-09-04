from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router


app = FastAPI(
    title="MediReach Voice Assistant"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "MediReach Medical AI Agent is running"
    }


def open_frontend():
    webbrowser.open(
        "http://127.0.0.1:8000/frontend/index.html"
    )


@app.on_event("startup")
async def startup_event():

    threading.Timer(
        1.0,
        open_frontend
    ).start()
