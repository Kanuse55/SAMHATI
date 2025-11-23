import pandas as pd
import os

DOCTORS_FILE = "doctors.csv"

def init_doctors_db():
    """Creates a dummy doctor database if missing."""
    if not os.path.exists(DOCTORS_FILE):
        data = {
            "username": ["Dr. Alex", "Dr. Smith", "Dr. House", "Dr. Joy", "Dr. Strange"],
            "specialty": ["Dermatology", "General Medicine", "Neurology", "Psychiatry", "Surgery"],
            "status": ["Available", "Available", "Busy", "Available", "Available"]
        }
        df = pd.DataFrame(data)
        df.to_csv(DOCTORS_FILE, index=False)

def get_all_doctors(search_query=None):
    """
    Returns all available doctors.
    If search_query is provided, filters by Name or Specialty.
    """
    if not os.path.exists(DOCTORS_FILE):
        init_doctors_db()
    
    df = pd.read_csv(DOCTORS_FILE)
    
    # 1. Filter for Availability first (Optional: remove this line if you want to show Busy docs too)
    # available = df[df['status'] == "Available"].copy() 
    available = df.copy() # Let's show everyone, but mark them as Busy/Available visually
    
    # 2. Apply Search Filter (if user typed something)
    if search_query:
        query = search_query.lower()
        # Check if query matches Name OR Specialty
        mask = (
            available['username'].str.lower().str.contains(query) | 
            available['specialty'].str.lower().str.contains(query)
        )
        available = available[mask]
        
    return available

def update_doctor_status(username, status):
    if not os.path.exists(DOCTORS_FILE): return False
    df = pd.read_csv(DOCTORS_FILE)
    if username in df['username'].values:
        df.loc[df['username'] == username, 'status'] = status
        df.to_csv(DOCTORS_FILE, index=False)
        return True
    return False

def register_doctor_profile(username, specialty):
    if not os.path.exists(DOCTORS_FILE): init_doctors_db()
    df = pd.read_csv(DOCTORS_FILE)
    if username not in df['username'].values:
        new_row = pd.DataFrame([{"username": username, "specialty": specialty, "status": "Available"}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DOCTORS_FILE, index=False)