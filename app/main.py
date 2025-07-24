# backend/main.py
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv

# Import database utilities and models
from models.database import create_db_and_tables, engine, get_session

# Import MCP tool routers
from mcp.appointment_tools import router as appointment_router
from mcp.doctor_tools import router as doctor_router

# Load environment variables from .env file
load_dotenv()

# --- FastAPI Application Setup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application startup and shutdown events.
    Creates database tables and adds initial data on startup.
    """
    print("Creating database tables and adding initial data if needed...")
    create_db_and_tables()
    # Initial data addition is now handled within create_db_and_tables
    yield
    print("Application shutdown.")

app = FastAPI(
    title="Doctor Appointment and Reporting Assistant Backend",
    description="Backend for managing doctor appointments and generating reports using MCP-like tools, structured for clarity and scalability.",
    version="1.0.0",
    lifespan=lifespan
)

# Include MCP tool routers
app.include_router(appointment_router, prefix="/tools", tags=["Appointment Tools"])
app.include_router(doctor_router, prefix="/tools", tags=["Doctor Tools"])

# --- Root Endpoint ---
@app.get("/", summary="Health Check")
async def read_root():
    """Basic health check endpoint to confirm the backend is running."""
    return {"message": "Doctor Appointment Backend is running!"}

