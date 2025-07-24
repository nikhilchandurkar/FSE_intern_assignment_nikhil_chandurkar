# backend/mcp/doctor_tools.py
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from models.database import get_session, Doctor, Patient, Appointment

router = APIRouter()

# --- Pydantic Models for Requests and Responses ---
class GetAppointmentSummaryRequest(BaseModel):
    doctor_name: str
    start_date: Optional[date] = None # YYYY-MM-DD
    end_date: Optional[date] = None   # YYYY-MM-DD
    status_filter: Optional[str] = None # e.g., "booked", "completed", "cancelled"
    # Optional: Add a filter for patient conditions if such data were stored

class AppointmentSummaryResponse(BaseModel):
    doctor_name: str
    total_appointments: int
    appointments_by_status: Dict[str, int]
    patients_visited: List[str] # Names of patients
    message: str

# --- MCP Tool 3: Get Appointment Summary (for Doctor) ---
@router.post("/get_appointment_summary", response_model=AppointmentSummaryResponse, summary="Get a summary report of doctor's appointments")
async def get_appointment_summary(
    request: GetAppointmentSummaryRequest,
    session: Session = Depends(get_session)
):
    """
    Generates a summary report for a doctor's appointments within a specified date range
    and filters by status. This report can be used for doctor notifications.
    """
    doctor = session.exec(select(Doctor).where(Doctor.name == request.doctor_name)).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor '{request.doctor_name}' not found. Please provide a valid doctor name."
        )

    query = select(Appointment).where(Appointment.doctor_id == doctor.id)

    if request.start_date:
        query = query.where(Appointment.start_time >= datetime.combine(request.start_date, datetime.min.time()))
    if request.end_date:
        # Add one day to end_date to include appointments on the end_date itself
        query = query.where(Appointment.start_time < datetime.combine(request.end_date + timedelta(days=1), datetime.min.time()))
    if request.status_filter:
        query = query.where(Appointment.status == request.status_filter)

    appointments = session.exec(query).all()

    total_appointments = len(appointments)
    appointments_by_status: Dict[str, int] = {}
    patients_visited_ids = set() # Use a set to store unique patient IDs

    for appt in appointments:
        appointments_by_status[appt.status] = appointments_by_status.get(appt.status, 0) + 1
        if appt.status == "completed": # Assuming "completed" means the patient visited
            patients_visited_ids.add(appt.patient_id)

    patients_visited_names = []
    if patients_visited_ids:
        # Fetch patient names for the unique IDs
        patients = session.exec(select(Patient).where(Patient.id.in_(list(patients_visited_ids)))).all()
        patients_visited_names = [p.name for p in patients]

    message = (
        f"Summary for Dr. {request.doctor_name}:\n"
        f"Total appointments found: {total_appointments}\n"
        f"Appointments by status: {appointments_by_status}\n"
        f"Unique patients visited (completed appointments): {', '.join(patients_visited_names) if patients_visited_names else 'None'}"
    )

    # Mock notification mechanism (e.g., Slack/WhatsApp)
    print(f"\nMOCK: Sending doctor summary notification via external service:\n{message}\n")
    # In a real scenario, you would integrate with Slack/WhatsApp API here.

    return AppointmentSummaryResponse(
        doctor_name=request.doctor_name,
        total_appointments=total_appointments,
        appointments_by_status=appointments_by_status,
        patients_visited=patients_visited_names,
        message=message
    )

