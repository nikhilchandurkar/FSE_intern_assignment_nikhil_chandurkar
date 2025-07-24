# app/models/database.py
import os
from typing import Optional
from datetime import datetime

from sqlmodel import Field, SQLModel, create_engine, Session, select
from dotenv import load_dotenv # Import load_dotenv here

# Load environment variables to ensure DATABASE_URL is available
load_dotenv()

# --- Database Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/doctordb")
engine = create_engine(DATABASE_URL, echo=True)

# --- Models ---
class Doctor(SQLModel, table=True):
    """Represents a doctor in the system."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True) # Ensure doctor names are unique
    specialty: str

class Patient(SQLModel, table=True):
    """Represents a patient in the system."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True) # EmailStr is for Pydantic validation, use str for SQLModel

class Appointment(SQLModel, table=True):
    """Represents a doctor's appointment."""
    id: Optional[int] = Field(default=None, primary_key=True)
    doctor_id: int = Field(foreign_key="doctor.id")
    patient_id: int = Field(foreign_key="patient.id")
    start_time: datetime = Field(index=True)
    end_time: datetime
    status: str = Field(default="booked") # e.g., "booked", "completed", "cancelled"
    notes: Optional[str] = None

def create_db_and_tables():
    """
    Creates database tables based on SQLModel metadata.
    Adds initial doctor data if no doctors exist.
    """
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Add some initial data for testing if tables are empty
        if not session.exec(select(Doctor)).first():
            dr_ahuja = Doctor(name="Dr. Ahuja", specialty="General Physician")
            dr_smith = Doctor(name="Dr. Smith", specialty="Pediatrician")
            session.add(dr_ahuja)
            session.add(dr_smith)
            session.commit()
            session.refresh(dr_ahuja)
            session.refresh(dr_smith)
            print(f"Added initial doctors: {dr_ahuja.name}, {dr_smith.name}")
        else:
            print("Doctors already exist in the database.")

def get_session():
    """Dependency to get a database session."""
    with Session(engine) as session:
        yield session

