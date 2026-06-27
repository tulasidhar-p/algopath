import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, curriculum

app = FastAPI(
    title="AlgoPath API",
    description="Backend API for the AlgoPath Multi-Domain Study Planner Platform",
    version="1.0.0"
)

# Enable CORS for frontend Vite app
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
env_origins = os.getenv("CORS_ALLOWED_ORIGINS")
if env_origins:
    origins.extend([o.strip() for o in env_origins.split(",")])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints
app.include_router(auth.router)
app.include_router(curriculum.router)

@app.get("/")
def read_root():
    return {
        "success": True,
        "message": "AlgoPath API is running. Visit /docs for Swagger documentation."
    }
