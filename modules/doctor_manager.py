import pandas as pd
import os
import streamlit as st

DOCTORS_FILE = "doctors.csv"

# Simple mapping of Conditions to Specialties
# In a real app, this would be a large database.
SPECIALTY_MAP = {
    "Acne": "Dermatology",
    "Fever": "General Medicine",
    "Pain": "General Medicine",
    "Depression": "Psychiatry",
    "Anxiety": "Psychiatry",
    "Diabetes": "Endocrinology",
    "Infection": "General Medicine"
}

def init_doctors_db():
    """Creates doctors.csv if it doesn't exist."""
    if not os.path.exists(DOCTORS_FILE):
        # Create dummy data for testing
        data = {
            "username": ["dr_skin", "dr_general", "dr_mind"],
            "specialty": ["Dermatology", "General Medicine", "Psychiatry"],
            "status": ["Available", "Busy", "Available"]
        }
        df = pd.DataFrame(data)
        df.to_csv(DOCTORS_FILE, index=False)

def get_doctor_specialty(condition):
    """Finds which specialist handles a specific condition."""
    for key, val in SPECIALTY_MAP.items():
        if key.lower() in condition.lower():
            return val
    return "General Medicine" # Default fallback

def get_available_doctors(specialty):
    """Returns a list of available doctors for a specialty."""
    if not os.path.exists(DOCTORS_FILE):
        init_doctors_db()
    
    df = pd.read_csv(DOCTORS_FILE)
    
    # Filter by Specialty AND Availability
    # We use string matching to be safe
    available = df[
        (df['specialty'] == specialty) & 
        (df['status'] == "Available")
    ]
    return available

def update_doctor_status(username, status):
    """Updates a doctor's availability (Available/Busy)."""
    if not os.path.exists(DOCTORS_FILE):
        init_doctors_db()
        
    df = pd.read_csv(DOCTORS_FILE)
    
    if username in df['username'].values:
        df.loc[df['username'] == username, 'status'] = status
        df.to_csv(DOCTORS_FILE, index=False)
        return True
    return False

def register_doctor_profile(username, specialty):
    """Adds a new doctor to the specific doctors database."""
    if not os.path.exists(DOCTORS_FILE):
        init_doctors_db()
        
    df = pd.read_csv(DOCTORS_FILE)
    
    if username not in df['username'].values:
        new_row = pd.DataFrame([{"username": username, "specialty": specialty, "status": "Available"}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DOCTORS_FILE, index=False)