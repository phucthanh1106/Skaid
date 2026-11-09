from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.messages import message_router

# Define cors origins
origins = [
    "http://localhost:5173"
]

# Create the application and register its HTTP configuration.
app = FastAPI()
app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)
app.include_router(message_router)
