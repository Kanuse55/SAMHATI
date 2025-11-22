import pandas as pd
import os
import datetime

APPOINTMENTS_FILE = "appointments.csv"

def init_appointments_db():
    if not os.path.exists(APPOINTMENTS_FILE):
        df = pd.DataFrame(columns=["id", "patient", "doctor", "condition", "status", "timestamp"])
        df.to_csv(APPOINTMENTS_FILE, index=False)

def request_appointment(patient, doctor, condition):
    init_appointments_db()
    df = pd.read_csv(APPOINTMENTS_FILE)
    
    # Generate a simple ID
    new_id = len(df) + 1
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    new_row = pd.DataFrame([{
        "id": new_id,
        "patient": patient,
        "doctor": doctor,
        "condition": condition,
        "status": "Pending",
        "timestamp": timestamp
    }])
    
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(APPOINTMENTS_FILE, index=False)
    return True

def get_doctor_appointments(doctor_name):
    init_appointments_db()
    df = pd.read_csv(APPOINTMENTS_FILE)
    # Return appointments for this doctor (newest first)
    return df[df['doctor'] == doctor_name].sort_values(by="id", ascending=False)

def update_status(appt_id, new_status):
    df = pd.read_csv(APPOINTMENTS_FILE)
    df.loc[df['id'] == appt_id, 'status'] = new_status
    df.to_csv(APPOINTMENTS_FILE, index=False)