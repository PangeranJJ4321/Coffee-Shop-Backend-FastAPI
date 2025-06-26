from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware 
import os
from app.core.database import Base, engine
from app.routes import api
from app.core.config import settings

# Create application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# if not os.path.exists("uploads"):
#     os.makedirs("uploads")

# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://coffee-shop-app-fix-yaak.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(TrustedHostMiddleware, allowed_hosts=["coffee-shop-backend-fastapi-production.up.railway.app"])


# Include API router
app.include_router(api.api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to Coffee Shop API"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)