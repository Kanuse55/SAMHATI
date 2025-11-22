import streamlit as st
import pandas as pd
import bcrypt
import os

USERS_FILE = "users.csv"

def init_users_db():
    """Creates the users.csv file if it doesn't exist."""
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=["username", "password", "role"])
        # Create a default admin account
        # Password is 'admin123'
        hashed_pw = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Using pd.concat instead of append (deprecated)
        new_row = pd.DataFrame([{"username": "admin", "password": hashed_pw, "role": "admin"}])
        df = pd.concat([df, new_row], ignore_index=True)
        
        df.to_csv(USERS_FILE, index=False)

def load_users():
    """Loads the users database."""
    if not os.path.exists(USERS_FILE):
        init_users_db()
    return pd.read_csv(USERS_FILE)

def signup_user(username, password, role="patient"):
    """Registers a new user."""
    users = load_users()
    
    if username in users['username'].values:
        return False, "Username already exists!"
    
    # Hash the password
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    new_user = pd.DataFrame([{"username": username, "password": hashed_pw, "role": role}])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv(USERS_FILE, index=False)
    
    return True, "Account created successfully! Please login."

def login_user(username, password):
    """Verifies credentials."""
    users = load_users()
    
    user_row = users[users['username'] == username]
    
    if user_row.empty:
        return None, "User not found."
    
    stored_hash = user_row.iloc[0]['password']
    
    # Verify password
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return user_row.iloc[0].to_dict(), "Success"
    else:
        return None, "Incorrect password."