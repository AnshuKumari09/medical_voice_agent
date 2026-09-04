from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import webbrowser
import threading

from app.api.routes.chat import router as chat_router


app = FastAPI(
    title="MediReach Medical AI Agent",
    version="1.0.0"
)


# Serve frontend
app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)


# API routes
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