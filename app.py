import streamlit as st
import pandas as pd
import plotly.express as px
import os
from modules import auth, model, chatbot, doctor_manager, appointments, predictor

# -----------------------------------------------------------------------------
# 1. SETUP & THEME
# -----------------------------------------------------------------------------
st.set_page_config(page_title="SAMHATI", page_icon="🏥", layout="wide")

# --- PASTE YOUR TOKEN HERE ---
GITHUB_TOKEN = "PASTE_YOUR_TOKEN_HERE" 

# CSS Styling
# CSS Styling: Fixes Admin Metrics & Tab Borders
st.markdown("""
<style>
    /* Force Global Background to Light */
    .stApp { background-color: #f0f2f5; color: #333333; }
    h1, h2, h3, h4, p, li { color: #0e1117; }
    
    /* --- FIX ADMIN METRICS (Invisible Numbers) --- */
    div[data-testid="stMetricValue"] {
        font-size: 36px !important;
        color: #008080 !important; /* Force Teal Color */
        font-weight: bold !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 16px !important;
        color: #333333 !important; /* Force Dark Label */
    }

    /* --- BUTTONS (Teal Theme) --- */
    div.stButton > button:first-child {
        background-color: #008080 !important; color: #ffffff !important; 
        border-radius: 8px; border: none; font-weight: bold; padding: 10px 24px;
    }
    div.stButton > button:first-child:hover { background-color: #006666 !important; }

    /* --- TABS (Login, Signup, Users, Doctors) --- */
    /* 1. Container spacing */
    div[data-baseweb="tab-list"] {
        gap: 5px; 
        background-color: transparent; /* Remove ugly line container */
    }
    
    /* 2. Unselected Tab (Clean Grey Pill) */
    div[data-baseweb="tab-list"] button[data-baseweb="tab"] {
        background-color: #e0e0e0 !important; 
        color: #333333 !important;           
        border-radius: 10px 10px 0 0 !important; /* Rounded top corners */
        border: none !important;
        padding: 10px 20px !important;
        font-weight: 600;
    }
    
    /* 3. Selected Tab (Teal Pill) */
    div[data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #008080 !important; 
        color: #ffffff !important;
        border-radius: 10px 10px 0 0 !important;
    }

    /* CHAT BUBBLES */
    .user-bubble { background-color: #007bff; color: white !important; padding: 10px 15px; border-radius: 15px 15px 0 15px; float: right; margin: 5px; max-width: 70%; }
    .bot-bubble { background-color: white; color: black !important; padding: 10px 15px; border-radius: 15px 15px 15px 0; float: left; margin: 5px; border: 1px solid #ccc; max-width: 70%; }
    
    .landing-header { background: linear-gradient(90deg, #2E7D32 0%, #004d40 100%); padding: 40px; color: white; text-align: center; border-radius: 0 0 20px 20px; margin-bottom: 20px; }
    .landing-header h1 { color: white !important; }
    .landing-header p { color: #e8f5e9 !important; }
</style>
""", unsafe_allow_html=True)

if 'view' not in st.session_state: st.session_state.view = "AI Chat"
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

def logout():
    st.session_state.user = None
    st.session_state.chat_history = []
    st.session_state.view = "AI Chat"
    st.rerun()

# Load Data & Models
df = model.load_data()
doctor_manager.init_doctors_db()
predictor.load_models() 

# -----------------------------------------------------------------------------
# 2. ADMIN DASHBOARD
# -----------------------------------------------------------------------------
def admin_dashboard():
    st.markdown("## 🛡️ Admin Control Panel")
    col_head, col_out = st.columns([6, 1])
    with col_head: st.caption(f"Logged in as: {st.session_state.user['username']}")
    with col_out: 
        if st.button("Logout"): logout()
    st.markdown("---")

    users = auth.load_users()
    docs_df = pd.DataFrame()
    if os.path.exists("doctors.csv"): docs_df = pd.read_csv("doctors.csv")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Users", len(users))
    with c2: st.metric("Doctors", len(docs_df))
    with c3: st.metric("Drugs DB", len(df))
    with c4: st.metric("Reviews", f"{df['no_of_reviews'].sum():,.0f}")

    tab1, tab2 = st.tabs(["Users", "Doctors"])
    with tab1: st.dataframe(users, use_container_width=True)
    with tab2: st.dataframe(docs_df, use_container_width=True)

# -----------------------------------------------------------------------------
# 3. DOCTOR DASHBOARD (Updated: Refresh & Delete)
# -----------------------------------------------------------------------------
def doctor_dashboard():
    doc_name = st.session_state.user['username']
    
    # --- HEADER with REFRESH ---
    c1, c2, c3 = st.columns([5, 1, 1])
    with c1: st.markdown(f"## 🩺 Dr. {doc_name}")
    with c2: 
        if st.button("🔄 Refresh"): st.rerun() # Simple Refresh
    with c3: 
        if st.button("🚪 Logout"): logout()
    st.markdown("---")
    
    # --- 1. STATUS SETTINGS ---
    st.subheader("⚙️ Availability Settings")
    col_status, col_btn = st.columns([4, 1])
    
    with col_status:
        new_status = st.radio("Current Status:", ["Available", "Busy"], horizontal=True)
    
    with col_btn:
        st.write("") 
        if st.button("Update Status", use_container_width=True):
            doctor_manager.update_doctor_status(doc_name, new_status)
            st.success(f"Status updated to: {new_status}")

    st.markdown("---")
    
    # --- 2. APPOINTMENT MANAGEMENT ---
    st.subheader("📅 Schedule Management")
    
    appts = appointments.get_doctor_appointments(doc_name)
    
    if not appts.empty:
        pending_appts = appts[appts['status'] == 'Pending']
        confirmed_appts = appts[appts['status'] == 'Accepted']
        
        tab1, tab2 = st.tabs([f"🔔 Requests ({len(pending_appts)})", f"✅ Confirmed ({len(confirmed_appts)})"])
        
        # --- PENDING ---
        with tab1:
            if not pending_appts.empty:
                for index, row in pending_appts.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div style="background-color: white; padding: 15px; border-left: 5px solid #ffc107; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px;">
                            <h4 style="margin:0; color: #856404;">👤 {row['patient']}</h4>
                            <p style="margin:0; color: #555;"><b>Reason:</b> {row['condition']}</p>
                            <p style="margin:0; font-size: 12px; color: #888;">🕒 Requested: {row['timestamp']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        c_a, c_b, c_c = st.columns([1, 1, 4])
                        with c_a: 
                            if st.button("✅ Accept", key=f"acc_{row['id']}"): 
                                appointments.update_status(row['id'], "Accepted"); st.rerun()
                        with c_b: 
                            if st.button("❌ Reject", key=f"rej_{row['id']}"): 
                                appointments.update_status(row['id'], "Rejected"); st.rerun()
                        with c_c:
                            if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                                appointments.delete_appointment(row['id']); st.rerun()
            else:
                st.info("No pending requests.")

        # --- CONFIRMED ---
        with tab2:
            if not confirmed_appts.empty:
                for index, row in confirmed_appts.iterrows():
                    st.markdown(f"""
                    <div style="background-color: white; padding: 15px; border-left: 5px solid #28a745; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px;">
                        <h4 style="margin:0; color: #155724;">✅ Patient: {row['patient']}</h4>
                        <p style="margin:0; color: #333;"><b>Condition:</b> {row['condition']}</p>
                        <p style="margin:0; font-size: 12px; color: #888;">📅 Booked on: {row['timestamp']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑️ Cancel / Clear", key=f"done_{row['id']}"):
                        appointments.delete_appointment(row['id']); st.rerun()
            else:
                st.info("No confirmed appointments.")
    else:
        st.info("No appointment history found.")

# -----------------------------------------------------------------------------
# 4. PATIENT DASHBOARD (HUB MENU STYLE)
# -----------------------------------------------------------------------------
def patient_dashboard():
    # Initialize View to Menu if not set
    if 'view' not in st.session_state:
        st.session_state.view = "Menu"

    # --- TOP HEADER (Persistent) ---
    h1, h2 = st.columns([6, 1])
    with h1: 
        st.markdown(f"### 👤 Welcome, {st.session_state.user['username']}")
    with h2: 
        if st.button("🚪 Logout", use_container_width=True): logout()
            
    st.markdown("---") 

    # ============================================================
    # VIEW 0: THE MAIN MENU (HUB)
    # ============================================================
    if st.session_state.view == "Menu":
        st.subheader("What would you like to do today?")
        st.write("") # Spacer
        
        # 3 Large Option Cards
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.info("🤖 **Check Symptoms**")
            st.caption("Chat with AI to analyze symptoms & get drug recommendations.")
            if st.button("💬 Start Chat", use_container_width=True):
                st.session_state.view = "AI Chat"
                st.rerun()
                
        with c2:
            st.success("🩺 **Consult Doctor**")
            st.caption("Search for specialists and book an appointment.")
            if st.button("🔍 Find Doctor", use_container_width=True):
                st.session_state.view = "Consult Doctor"
                st.rerun()
                
        with c3:
            st.warning("📅 **My History**")
            st.caption("View your past and upcoming appointments.")
            if st.button("📂 View Appointments", use_container_width=True):
                st.session_state.view = "My Appointments"
                st.rerun()

    # ============================================================
    # VIEW 1: AI CHAT
    # ============================================================
    elif st.session_state.view == "AI Chat":
        # Back Button
        if st.button("⬅️ Back to Menu"):
            st.session_state.view = "Menu"
            st.rerun()
            
        st.subheader("💬 AI Health Assistant")
        
        # Chat History
        with st.container():
            for msg in st.session_state.chat_history:
                css = "user-bubble" if msg["role"] == "user" else "bot-bubble"
                st.markdown(f"<div style='overflow:hidden'><div class='{css}'>{msg['content']}</div></div>", unsafe_allow_html=True)
        
        user_input = st.chat_input("Describe your symptoms...")
        
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            condition = predictor.predict_condition(user_input)
            recs = pd.DataFrame()
            if condition != "General":
                recs = model.get_recommendations(condition, df)
                st.session_state.current_recs = recs 
            else:
                st.session_state.current_recs = pd.DataFrame()
                
            ai_reply = chatbot.get_ai_response(GITHUB_TOKEN, user_input, recs, st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            st.rerun()

        if 'current_recs' in st.session_state and not st.session_state.current_recs.empty:
            st.markdown("### 📊 Drug Analysis")
            recs_df = st.session_state.current_recs
            tab1, tab2 = st.tabs(["Top Drugs", "Popularity Graph"])
            with tab1: st.dataframe(recs_df[['drug_name', 'rating', 'no_of_reviews', 'side_effects']].head(5), use_container_width=True)
            with tab2:
                if 'no_of_reviews' in recs_df.columns and 'rating' in recs_df.columns:
                    fig = px.scatter(recs_df, x="no_of_reviews", y="rating", size="no_of_reviews", color="trust_score", hover_name="drug_name", title="Drug Effectiveness")
                    st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # VIEW 2: CONSULT DOCTOR
    # ============================================================
    elif st.session_state.view == "Consult Doctor":
        if st.button("⬅️ Back to Menu"):
            st.session_state.view = "Menu"
            st.rerun()

        st.subheader("🩺 Specialist Directory")
        
        c1, c2 = st.columns([3, 1])
        with c1:
            search_term = st.text_input("🔍 Search by Specialist or Name:", placeholder="e.g. Dermatologist, Dr. Alex")
        with c2:
            st.write("")
            st.write("")
            show_all = st.checkbox("Show All", value=True)

        if search_term: docs = doctor_manager.get_all_doctors(search_term)
        elif show_all: docs = doctor_manager.get_all_doctors()
        else: docs = pd.DataFrame()

        if not docs.empty:
            st.info(f"Found {len(docs)} doctors.")
            for _, doc in docs.iterrows():
                status_color = "green" if doc['status'] == "Available" else "red"
                with st.container():
                    col_info, col_action = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"""
                        <div style="padding:10px; border-left: 5px solid {status_color}; background-color: #f9f9f9; border-radius: 5px;">
                            <h4 style="margin:0; color:black;">👨‍⚕️ {doc['username']}</h4>
                            <p style="margin:0; color:#555;"><b>Specialty:</b> {doc['specialty']}</p>
                            <p style="margin:0; font-size:12px;">Status: <span style="color:{status_color}; font-weight:bold;">● {doc['status']}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_action:
                        st.write("")
                        if doc['status'] == "Available":
                            if st.button(f"📅 Book", key=doc['username']):
                                reason = search_term if search_term else f"Consultation: {doc['specialty']}"
                                if appointments.request_appointment(st.session_state.user['username'], doc['username'], reason):
                                    st.markdown(f"""<div style="background-color: #d4edda; padding: 10px; border-radius: 5px;"><h5 style="color: #155724; margin:0;">✅ Request Sent!</h5></div>""", unsafe_allow_html=True)
                        else:
                            st.button("Busy", disabled=True, key=doc['username'])
                    st.markdown("---")
        else:
            if search_term: st.warning("No doctors found.")
            else: st.info("Search to find a doctor.")

    # ============================================================
    # VIEW 3: MY APPOINTMENTS
    # ============================================================
    elif st.session_state.view == "My Appointments":
        if st.button("⬅️ Back to Menu"):
            st.session_state.view = "Menu"
            st.rerun()

        st.subheader("📅 My Appointments & History")
        
        my_appts = appointments.get_patient_appointments(st.session_state.user['username'])
        
        if not my_appts.empty:
            for index, row in my_appts.iterrows():
                status = row['status']
                if status == "Accepted": color, border = "#d4edda", "#28a745"
                elif status == "Rejected": color, border = "#f8d7da", "#dc3545"
                else: color, border = "#fff3cd", "#ffc107"
                
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: white; padding: 15px; border-left: 5px solid {border}; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px;">
                        <h4 style="margin:0; color: black;">👨‍⚕️ Dr. {row['doctor']}</h4>
                        <p style="margin:0; color: #555;"><b>Status:</b> <span style="color:{border}; font-weight:bold">{status}</span></p>
                        <p style="margin:0; color: #555;"><b>Reason:</b> {row['condition']}</p>
                        <p style="margin:0; font-size: 12px; color: #888;">📅 Time: {row['timestamp']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("❌ Cancel", key=f"pat_del_{row['id']}"):
                        appointments.delete_appointment(row['id'])
                        st.rerun()
        else:
            st.info("You have no appointment history.")

# -----------------------------------------------------------------------------
# 5. LANDING PAGE (UPDATED)
# -----------------------------------------------------------------------------
def landing_page():
    st.markdown("""<div class="landing-header"><h1>🏥 SAMHATI</h1><p>Intelligent Hybrid Medical Assistant</p></div>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        # --- LOGIN TAB ---
        with tab1:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            
            if st.button("Login", use_container_width=True):
                user, msg = auth.login_user(u, p)
                if user: 
                    st.session_state.user = user
                    st.session_state.view = "Menu"  # <--- THIS FIXES THE REDIRECT
                    st.rerun()
                else: 
                    st.error(msg)
        
        # --- SIGNUP TAB ---
        with tab2:
            nu = st.text_input("New User", key="s_u")
            np = st.text_input("New Pass", type="password", key="s_p")
            role = st.selectbox("Role", ["patient", "doctor"])
            
            # Show specialty only for doctors
            spec = "General"
            if role == "doctor":
                spec = st.selectbox("Specialty", ["General Medicine", "Dermatology", "Psychiatry", "Neurology", "Cardiology"])
            
            if st.button("Sign Up", use_container_width=True):
                success, msg = auth.signup_user(nu, np, role)
                if success: 
                    if role == "doctor": doctor_manager.register_doctor_profile(nu, spec)
                    st.success("Created! Login now.")
                else: st.error(msg)

if __name__ == "__main__":
    if st.session_state.user:
        if st.session_state.user['role'] == 'doctor': doctor_dashboard()
        elif st.session_state.user['role'] == 'admin': admin_dashboard()
        else: patient_dashboard()
    else: landing_page()