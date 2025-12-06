from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router

app = FastAPI(title="Financial News Intelligence API")

# Allow frontend or local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
