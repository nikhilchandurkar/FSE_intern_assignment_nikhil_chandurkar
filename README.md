Doctor Appointment and Reporting Assistant
This is a minimal full-stack web application demonstrating an agentic AI system for managing doctor appointments and generating reports. It integrates an LLM (simulated) with backend logic exposed via MCP-like tools (FastAPI endpoints), a PostgreSQL database, and includes a basic email service.

🎯 Objective
The primary objective is to showcase an AI agent's ability to dynamically discover and invoke tools to fulfill user prompts, supporting two main scenarios:

Patient Appointment Scheduling: Patients can schedule appointments based on doctor availability. The system confirms bookings via email.

Doctor Summary Report and Notification: Doctors can request summarized reports of their appointments, which would typically be sent via a notification mechanism (mocked in this version).

✨ Features
Doctor Availability Check: Patients can check a doctor's available time slots for a specific date.

Appointment Booking: Patients can book an available slot, with automatic patient creation if new.

Email Confirmation: Patients receive an email confirmation upon successful booking.

Doctor Appointment Summary: Doctors can retrieve reports on their appointments, filtered by date range and status.

Agentic AI Simulation: A conceptual Python script demonstrates how an LLM agent would interpret natural language and call the backend tools.

Modular Backend: Organized FastAPI application with clear separation of concerns (models, utilities, MCP tools).

Basic React Frontend: A simple UI to interact with the backend for both patient and doctor scenarios.

🔧 Tech Stack
Backend: FastAPI

Database: PostgreSQL (via SQLModel ORM)

Email Service: Python's smtplib (SMTP)

Environment Management: python-dotenv

Frontend: React JS

Styling: Tailwind CSS

Date/Time Handling: moment.js

LLM Integration (Conceptual): Python script simulating LLM agent behavior.

📁 Folder Structure
app/
├── main.py                     # FastAPI application entry point
├── .env                        # Environment variables (database, SMTP, Google API)
├── auth/                       # Placeholder for authentication utilities
│   └── auth_utils.py
├── models/                     # Database models and session management
│   └── database.py
├── utils/                      # Reusable utility functions
│   └── email_service.py
│   └── google_calendar_service.py # Placeholder for Google Calendar API
│   └── notification_service.py    # Placeholder for other notification services
├── mcp/                        # MCP-like tool definitions (FastAPI routers)
│   └── appointment_tools.py    # Endpoints for checking availability and booking
│   └── doctor_tools.py         # Endpoints for doctor summaries
├── llm_agent_simulation.py     # Conceptual script demonstrating LLM agent interaction
└── frontend/                   # React frontend application
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── App.js              # Main React component
    │   ├── index.js            # React entry point
    │   └── index.css           # Tailwind CSS imports
    ├── package.json
    └── tailwind.config.js

🚀 Setup and Running the Application
Prerequisites
Before you begin, ensure you have the following installed:

Python 3.9+: Download Python

Poetry (Recommended) or pip: For Python dependency management.

PostgreSQL: Download PostgreSQL

Ensure your PostgreSQL server is running.

Note your postgres user's password.

Node.js & npm (or Yarn): Download Node.js (npm comes with Node.js)

1. Backend Setup
Navigate to the app directory:

cd app

Create a Python Virtual Environment (if not already in one):

python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate # On macOS/Linux

Install Python Dependencies:

pip install fastapi uvicorn sqlmodel psycopg2-binary python-dotenv

Configure Environment Variables:

Create a file named .env in the app/ directory if it doesn't exist.

Populate it with your PostgreSQL and SMTP credentials. Crucially, ensure the DATABASE_URL uses your actual postgres user password and the correct database name.

# .env file for Doctor Appointment Backend

# PostgreSQL Database Configuration
# Replace '2523' with your actual PostgreSQL password for the 'postgres' user.
# The database 'doctordb' will be created automatically if it doesn't exist.
DATABASE_URL="postgresql://postgres:2523@localhost:5432/doctordb"

# JWT Authentication Configuration (for future login functionality)
SECRET_KEY="your_jwt_secret_key" # IMPORTANT: Generate a strong, random key
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SMTP Email Service Configuration (for sending appointment confirmations)
# Replace with your SMTP server details. For Gmail, you'll need an App Password if 2FA is enabled.
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587 # Common ports: 587 (TLS), 465 (SSL)
SMTP_USERNAME="nikhilchandurkar24@gmail.com"
SMTP_PASSWORD="your_email_app_password" # IMPORTANT: Your Gmail App Password
SENDER_EMAIL="nikhilchandurkar24@gmail.com" # Usually the same as SMTP_USERNAME

# Google API Configuration (for future Google Calendar integration)
GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
GOOGLE_REFRESH_TOKEN="your_refresh_token" # Required for offline access to Google APIs

Gmail App Password: If you use Gmail and have 2-Factor Authentication enabled, you must generate an "App password" for SMTP_PASSWORD. Your regular Gmail password will not work. Go to your Google Account -> Security -> App passwords.

Run the FastAPI Backend:

uvicorn main:app --reload

The backend will start on http://127.0.0.1:8000. It will attempt to create the doctordb database and the necessary tables on startup.

2. Frontend Setup
Open a new terminal and navigate to the frontend directory:

cd app/frontend

Install Node.js Dependencies:

npm install # or yarn install

Run the React Frontend:

npm start # or yarn start

The frontend will typically open in your browser at http://localhost:3000.

🧪 How to Test the Application
Once both the backend (FastAPI) and frontend (React) are running, you can test the functionalities.

A. Testing Backend Endpoints (Swagger UI)
Open your web browser and go to http://127.0.0.1:8000/docs. This will display the interactive API documentation (Swagger UI) where you can directly test the backend endpoints.

/tools/check_availability (POST):

Click "Try it out".

Provide doctor_name (e.g., "Dr. Ahuja" or "Dr. Smith") and a date (e.g., "2025-07-25").

Click "Execute" to see available slots.

/tools/book_appointment (POST):

Click "Try it out".

Provide doctor_name, patient_name, patient_email, and a start_time (e.g., "2025-07-25T10:00:00"). Ensure the start_time is one of the available slots you found.

Click "Execute". Check your provided patient_email for a confirmation email.

/tools/get_appointment_summary (POST):

Click "Try it out".

Provide doctor_name (e.g., "Dr. Ahuja"). You can optionally add start_date, end_date, or status_filter.

Click "Execute" to get a summary report. Check your backend console for the mock notification message.

B. Testing with the React Frontend
Open your web browser and go to http://localhost:3000.

Patient Portal:
Check Availability:

Enter a "Doctor's Name" (e.g., "Dr. Ahuja").

Select an "Appointment Date".

Click "Check Availability". Available slots will appear below.

Book Appointment:

Select one of the "Available Slots".

Enter "Your Name" and "Your Email".

Click "Book Selected Appointment". You should see a success message, and an email confirmation will be sent to the provided email address.

Doctor Portal:
Get Summary Report:

Enter a "Doctor's Name" (e.g., "Dr. Ahuja").

Optionally, select "Start Date", "End Date", or "Status Filter".

Click "Get Summary Report". The report will be displayed on the screen, and a mock notification message will appear in your backend console.

C. Testing with the LLM Agent Simulation (Conceptual)
This script simulates how an LLM would interact.

Ensure Backend is Running: Make sure your FastAPI backend is active in its terminal.

Run the Simulation Script:

cd app
python llm_agent_simulation.py

Interact with the simulated agent using natural language prompts:

Patient Scenario 1 (Check Availability):

I want to check Dr. Ahuja's availability for tomorrow.

Check Dr. Smith's availability for 2025-07-26.

Patient Scenario 2 (Book Appointment - Multi-turn):

First, set patient context: My name is Jane Doe and my email is jane.doe@example.com.

Then, check availability: I want to check Dr. Ahuja's availability for tomorrow. (Observe available slots).

Then, book: Please book the 3 PM slot for me. (The agent uses context for doctor, date, and patient details).

Alternatively, a single prompt: Book appointment with Dr. Ahuja for John Doe, john.doe@example.com at 2025-07-25T10:30:00.

Doctor Scenario (Summary Report):

How many appointments does Dr. Ahuja have today?

How many patients visited yesterday for Dr. Smith?

Give me a summary for Dr. Ahuja for the last week. (You might need to adjust the script's date parsing for complex ranges).

💡 Future Enhancements
Full Google Calendar Integration: Replace mock calls with actual Google Calendar API integration for scheduling.

Dedicated Notification Service: Implement integration with Slack, WhatsApp Business API, or Firebase Cloud Messaging for doctor reports.

Role-Based Login: Implement patient and doctor login using JWT (utilizing the auth/auth_utils.py and .env variables).

LLM Integration: Connect to a real LLM (e.g., OpenAI GPT, Gemini, Claude) to replace the simulated agent logic.

Auto-Rescheduling: Implement LLM-powered logic to suggest and handle appointment rescheduling.

Prompt History Tracking: Store and display conversation history for better context.

Improved Frontend UI/UX: Enhance the user interface for a more polished experience.

Dockerization: Containerize the backend and frontend for easier deployment.
