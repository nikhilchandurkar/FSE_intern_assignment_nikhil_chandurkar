# app/mcp/appointment_tools.py
from typing import List, Optional
from datetime import datetime, timedelta, date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from models.database import get_session, Doctor, Patient, Appointment
from utils.email_service import send_email
# from utils.google_calendar_service import create_calendar_event # Future integration

router = APIRouter()

# --- Pydantic Models for Requests and Responses ---
class CheckAvailabilityRequest(BaseModel):
    doctor_name: str
    date: date # YYYY-MM-DD
    duration_minutes: int = 30 # Default appointment duration

class AvailabilityResponse(BaseModel):
    doctor_name: str
    date: date
    available_slots: List[datetime]
    message: str

class BookAppointmentRequest(BaseModel):
    doctor_name: str
    patient_name: str
    patient_email: EmailStr
    start_time: datetime # YYYY-MM-DDTHH:MM:SS format
    duration_minutes: int = 30 # Default appointment duration
    notes: Optional[str] = None

class BookAppointmentResponse(BaseModel):
    appointment_id: int
    doctor_name: str
    patient_name: str
    start_time: datetime
    status: str
    message: str

# --- MCP Tool 1: Check Doctor Availability ---
@router.post("/check_availability", response_model=AvailabilityResponse, summary="Check a doctor's availability for a specific date")
async def check_doctor_availability(
    request: CheckAvailabilityRequest,
    session: Session = Depends(get_session)
):
    """
    Checks the availability of a doctor for a given date.
    Returns a list of available 30-minute slots within defined working hours (9 AM to 5 PM).
    """
    doctor = session.exec(select(Doctor).where(Doctor.name == request.doctor_name)).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor '{request.doctor_name}' not found. Please provide a valid doctor name."
        )

    # Define working hours (e.g., 9 AM to 5 PM)
    start_of_day = datetime.combine(request.date, datetime.min.time()).replace(hour=9, minute=0, second=0, microsecond=0)
    end_of_day = datetime.combine(request.date, datetime.min.time()).replace(hour=17, minute=0, second=0, microsecond=0)

    # Fetch existing booked appointments for the doctor on the given date
    appointments = session.exec(
        select(Appointment)
        .where(Appointment.doctor_id == doctor.id)
        .where(Appointment.start_time >= start_of_day)
        .where(Appointment.start_time < end_of_day + timedelta(days=1)) # Covers the entire day
        .where(Appointment.status == "booked") # Only consider booked appointments as unavailable
    ).all()

    booked_intervals = []
    for appt in appointments:
        booked_intervals.append((appt.start_time, appt.end_time))

    available_slots = []
    current_slot_start = start_of_day
    while current_slot_start + timedelta(minutes=request.duration_minutes) <= end_of_day:
        slot_end = current_slot_start + timedelta(minutes=request.duration_minutes)
        is_available = True
        for booked_start, booked_end in booked_intervals:
            # Check for overlap: if the new slot starts before booked_end AND ends after booked_start
            if not (slot_end <= booked_start or current_slot_start >= booked_end):
                is_available = False
                break
        if is_available:
            available_slots.append(current_slot_start)
        current_slot_start += timedelta(minutes=request.duration_minutes)

    message = f"Found {len(available_slots)} available slots for Dr. {request.doctor_name} on {request.date}."
    return AvailabilityResponse(
        doctor_name=request.doctor_name,
        date=request.date,
        available_slots=available_slots,
        message=message
    )

# --- MCP Tool 2: Book Appointment ---
@router.post("/book_appointment", response_model=BookAppointmentResponse, summary="Book an appointment for a patient with a doctor")
async def book_appointment(
    request: BookAppointmentRequest,
    session: Session = Depends(get_session)
):
    """
    Books an appointment for a patient with a specific doctor at a given time.
    Sends an email confirmation to the patient and integrates with Google Calendar (mocked).
    Handles patient creation if they don't exist and prevents double booking.
    """
    doctor = session.exec(select(Doctor).where(Doctor.name == request.doctor_name)).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor '{request.doctor_name}' not found. Please provide a valid doctor name."
        )

    patient = session.exec(select(Patient).where(Patient.email == request.patient_email)).first()
    if not patient:
        # Create new patient if not exists
        patient = Patient(name=request.patient_name, email=request.patient_email)
        session.add(patient)
        session.commit()
        session.refresh(patient)
        print(f"Created new patient: {patient.name} with email {patient.email}")

    end_time = request.start_time + timedelta(minutes=request.duration_minutes)

    # Validate if the requested start_time is within doctor's working hours
    start_of_day = datetime.combine(request.start_time.date(), datetime.min.time()).replace(hour=9, minute=0, second=0, microsecond=0)
    end_of_day = datetime.combine(request.start_time.date(), datetime.min.time()).replace(hour=17, minute=0, second=0, microsecond=0)

    if not (start_of_day <= request.start_time < end_of_day and start_of_day < end_time <= end_of_day + timedelta(minutes=1)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested appointment time {request.start_time.strftime('%H:%M')} is outside Dr. {doctor.name}'s working hours (9 AM - 5 PM)."
        )

    # Check for existing appointments that overlap (double booking prevention)
    overlapping_appointments = session.exec(
        select(Appointment)
        .where(Appointment.doctor_id == doctor.id)
        .where(Appointment.status == "booked")
        .where(
            (Appointment.start_time < end_time) & (Appointment.end_time > request.start_time)
        )
    ).all()

    if overlapping_appointments:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The requested slot is already booked or overlaps with an existing appointment. Please choose another time."
        )

    # --- Google Calendar API Integration Placeholder ---
    # In a real scenario, you would call Google Calendar API to schedule the event here.
    # This would involve:
    # 1. Authenticating with Google Calendar API (OAuth 2.0).
    # 2. Creating an event with doctor, patient, time, and description.
    # 3. Handling potential errors from the Google Calendar API.
    try:
        # calendar_event_id = create_calendar_event(
        #     doctor_email="doctor@example.com", # Replace with actual doctor email from DB
        #     patient_email=request.patient_email,
        #     start_time=request.start_time,
        #     end_time=end_time,
        #     summary=f"Appointment with Dr. {doctor.name} - {request.patient_name}",
        #     description=request.notes or "Patient appointment"
        # )
        print(f"MOCK: Google Calendar event created for Dr. {doctor.name} with {patient.name} at {request.start_time}")
        # new_appointment.calendar_event_id = calendar_event_id # Store if needed
    except Exception as e:
        print(f"WARNING: Failed to create Google Calendar event: {e}")
        # You might choose to still book the appointment in your DB but log the calendar failure
        # Or raise an HTTPException if calendar booking is critical.

    new_appointment = Appointment(
        doctor_id=doctor.id,
        patient_id=patient.id,
        start_time=request.start_time,
        end_time=end_time,
        status="booked",
        notes=request.notes
    )
    session.add(new_appointment)
    session.commit()
    session.refresh(new_appointment)

    # Send email confirmation
    email_subject = "Appointment Confirmation"
    email_body = (
        f"Dear {patient.name},\n\n"
        f"Your appointment with Dr. {doctor.name} has been successfully booked.\n"
        f"Date: {request.start_time.strftime('%Y-%m-%d')}\n"
        f"Time: {request.start_time.strftime('%H:%M')}\n"
        f"Duration: {request.duration_minutes} minutes\n\n"
        f"We look forward to seeing you!\n\n"
        f"Best regards,\nYour Clinic"
    )
    email_sent = send_email(patient.email, email_subject, email_body)

    message = f"Appointment booked successfully. Confirmation email {'sent' if email_sent else 'failed to send'}."
    return BookAppointmentResponse(
        appointment_id=new_appointment.id,
        doctor_name=doctor.name,
        patient_name=patient.name,
        start_time=new_appointment.start_time,
        status=new_appointment.status,
        message=message
    )

