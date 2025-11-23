import streamlit as st
import pandas as pd
import plotly.express as px
import os
from modules import auth, model, chatbot, doctor_manager, appointments

#Home page 

st.set_page_config(page_title="Drug Recommendation System", page_icon="🏥", layout="wide")

# paste token here
GITHUB_TOKEN = "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" 

# css
st.markdown("""
<style>
    /* Global Text Reset */
    .stApp { background-color: #f0f2f5; color: #333333; }
    h1, h2, h3, h4, p, li { color: #0e1117; }
    
    /* BUTTON STYLING (Standard Buttons) */
    div.stButton > button:first-child {
        background-color: #008080 !important; /* Teal Background */
        color: #ffffff !important;            /* White Text */
        border-radius: 8px;
        border: none;
        font-weight: bold;
        font-size: 16px;
        padding: 10px 24px;
    }
    div.stButton > button:first-child:hover {
        background-color: #006666 !important; /* Darker Teal on Hover */
        color: #ffffff !important;
    }

    /* --- FIX TABS STYLING (Login/Sign Up Red Box Issue) --- */
    /* 1. Unselected Tab (Light Grey) */
    div[data-baseweb="tab-list"] button[data-baseweb="tab"] {
        background-color: #e0e0e0 !important; 
        color: #333333 !important;           
        border-radius: 5px 5px 0 0;
        font-weight: 600;
        border: none !important;
    }
    
    /* 2. Selected Tab (Teal with White Text) */
    div[data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #008080 !important; 
        color: #ffffff !important;           
    }

    /* LANDING PAGE HEADER */
    .landing-header {
        background: linear-gradient(90deg, #2E7D32 0%, #004d40 100%);
        padding: 40px; color: white; text-align: center; border-radius: 0 0 20px 20px; margin-bottom: 20px;
    }
    .landing-header h1 { color: white !important; }
    .landing-header p { color: #e8f5e9 !important; }

    /* CHAT BUBBLES */
    .user-bubble { background-color: #007bff; color: white !important; padding: 10px 15px; border-radius: 15px 15px 0 15px; float: right; margin: 5px; max-width: 70%; }
    .bot-bubble { background-color: white; color: black !important; padding: 10px 15px; border-radius: 15px 15px 15px 0; float: left; margin: 5px; border: 1px solid #ccc; max-width: 70%; }
    
    /* NAVIGATION MENU (Top Bar) */
    .nav-container { display: flex; justify-content: center; gap: 20px; padding-bottom: 20px; border-bottom: 1px solid #ddd; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# Ensure session state for Navigation View exists
if 'view' not in st.session_state: st.session_state.view = "AI Chat"

# Session Init
if 'user' not in st.session_state: st.session_state.user = None
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

def logout():
    st.session_state.user = None
    st.session_state.chat_history = []
    st.session_state.view = "AI Chat" # Reset view
    st.rerun()

# Load data
df = model.load_data()
doctor_manager.init_doctors_db()

# admin acess

def admin_dashboard():
    st.markdown("## 🛡️ Admin Control Panel")
    
    # Top Bar with Logout
    col_head, col_out = st.columns([6, 1])
    with col_head: st.caption(f"System Status: Online | Logged in as: {st.session_state.user['username']}")
    with col_out: 
        if st.button("Logout"): logout()
    
    st.markdown("---")

    # 1. SYSTEM METRICS
    users = auth.load_users()
    
    # Load Doctors CSV directly for stats
    docs_df = pd.DataFrame()
    if os.path.exists("doctors.csv"):
        docs_df = pd.read_csv("doctors.csv")

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Users", len(users))
    with col2: st.metric("Doctors Onboarded", len(docs_df))
    with col3: st.metric("Drugs in DB", len(df))
    with col4: st.metric("Total Reviews", f"{df['no_of_reviews'].sum():,.0f}")

    # 2. DATA VISUALIZATION & TABLES
    tab1, tab2, tab3 = st.tabs(["👥 User Base", "🩺 Doctor Network", "💊 Drug Database"])

    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            # Pie Chart of Roles
            role_counts = users['role'].value_counts().reset_index()
            role_counts.columns = ['Role', 'Count']
            fig = px.pie(role_counts, values='Count', names='Role', title='User Role Distribution', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("Registered Users Log")
            st.dataframe(users, use_container_width=True)

    with tab2:
        st.subheader("Doctor Availability & Specialty")
        if not docs_df.empty:
            st.dataframe(docs_df, use_container_width=True)
            
            # Bar chart of specialties
            spec_counts = docs_df['specialty'].value_counts().reset_index()
            fig2 = px.bar(spec_counts, x='specialty', y='count', title="Doctors by Specialty", color='specialty')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No doctors registered yet.")

    with tab3:
        st.subheader("Pharma Database Preview")
        st.dataframe(df.head(100), use_container_width=True)

# doctor acess
def doctor_dashboard():
    doc_name = st.session_state.user['username']
    
    # --- TOP NAV ---
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown(f"## 🩺 Dashboard: Dr. {doc_name}")
    with c2:
        if st.button("🚪 Logout", use_container_width=True): logout()
        
    st.markdown("---")
    
    # 1. Availability Section
    st.info("💡 Tip: Set your status to 'Available' to receive new patients.")
    
    # 2. Appointment Management
    st.subheader("📅 Appointment Requests")
    
    appts = appointments.get_doctor_appointments(doc_name)
    
    if not appts.empty:
        for index, row in appts.iterrows():
            # Card Styling
            card_color = "#fff3cd" if row['status'] == "Pending" else "#d4edda"
            border_color = "#ffc107" if row['status'] == "Pending" else "#28a745"
            
            with st.container():
                st.markdown(f"""
                <div style="background-color:{card_color}; padding:15px; border-left:5px solid {border_color}; border-radius:5px; margin-bottom:10px; color:black;">
                    <h4 style="margin:0; color:black;">👤 Patient: {row['patient']}</h4>
                    <p style="margin:0; color:#333;"><b>Condition:</b> {row['condition']}</p>
                    <p style="margin:0; color:#333;"><b>Status:</b> {row['status']} | <b>Time:</b> {row['timestamp']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Buttons (Only show if Pending)
                if row['status'] == "Pending":
                    c_a, c_b = st.columns([1, 4])
                    with c_a:
                        if st.button("✅ Accept", key=f"acc_{row['id']}"):
                            appointments.update_status(row['id'], "Accepted")
                            st.rerun()
                    with c_b:
                        if st.button("❌ Reject", key=f"rej_{row['id']}"):
                            appointments.update_status(row['id'], "Rejected")
                            st.rerun()
    else:
        st.write("No appointments found.")

# patien acess
def patient_dashboard():
    # --- TOP HEADER (Static Logout) ---
    h1, h2 = st.columns([6, 1])
    with h1:
        st.markdown(f"### 👤 Welcome, {st.session_state.user['username']}")
    with h2:
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            
    
    # Switches view between Chat and Consult
    if st.session_state.view == "AI Chat":
        if st.button("🩺 Consult a Doctor Instead", use_container_width=True):
            st.session_state.view = "Consult Doctor"
            st.rerun()
    else:
        if st.button("💬 Back to AI Assistant", use_container_width=True):
            st.session_state.view = "AI Chat"
            st.rerun()

    st.markdown("---") 

    # --- VIEW 1: AI CHAT ---
    if st.session_state.view == "AI Chat":
        st.subheader("💬 AI Health Assistant")
        
        # 1. Display Chat History
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                css = "user-bubble" if msg["role"] == "user" else "bot-bubble"
                st.markdown(f"<div style='overflow:hidden'><div class='{css}'>{msg['content']}</div></div>", unsafe_allow_html=True)
        
        # 2. Chat Input
        user_input = st.chat_input("Ask about drugs or symptoms...")
        
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Extract Condition
            condition = chatbot.extract_condition_with_ai(GITHUB_TOKEN, user_input)
            
            recs = pd.DataFrame()
            if condition != "General":
                recs = model.get_recommendations(condition, df)
                st.session_state.current_recs = recs 
            else:
                st.session_state.current_recs = pd.DataFrame() 
                
            # Get AI Response
            ai_reply = chatbot.get_ai_response(GITHUB_TOKEN, user_input, recs, st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            st.rerun()

        # 3. RECOMMENDATION GRAPHS
        if 'current_recs' in st.session_state and not st.session_state.current_recs.empty:
            st.markdown("### 📊 Drug Analysis")
            recs_df = st.session_state.current_recs
            
            tab1, tab2 = st.tabs(["💊 Top Drugs", "📈 Popularity Graph"])
            with tab1:
                st.dataframe(recs_df[['drug_name', 'rating', 'no_of_reviews', 'side_effects']].head(5), use_container_width=True)
            with tab2:
                if 'no_of_reviews' in recs_df.columns and 'rating' in recs_df.columns:
                    fig = px.scatter(
                        recs_df, x="no_of_reviews", y="rating", 
                        size="no_of_reviews", color="trust_score", 
                        hover_name="drug_name", title="Drug Effectiveness"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Not enough data to plot graph.")

    # --- VIEW 2: CONSULT DOCTOR ---
    elif st.session_state.view == "Consult Doctor":
        st.subheader("🩺 Find a Specialist")
        condition = st.text_input("Enter your condition (e.g., Acne, Fever)")
        
        if condition:
            specialty = doctor_manager.get_doctor_specialty(condition)
            st.success(f"Recommended Specialist: **{specialty}**")
            
            docs = doctor_manager.get_available_doctors(specialty)
            
            if not docs.empty:
                for _, doc in docs.iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div style="background:white; padding:15px; border-radius:10px; border:1px solid #ddd; margin-bottom:10px;">
                            <h4 style="color:black; margin:0;">👨‍⚕️ Dr. {doc['username']}</h4>
                            <p style="color:green; margin:0;">● Available for Consultation</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"Request Appointment with Dr. {doc['username']}", key=doc['username']):
                            if appointments.request_appointment(st.session_state.user['username'], doc['username'], condition):
                                st.success(f"✅ Request Sent to Dr. {doc['username']}!")
            else:
                st.warning("No doctors currently available.")

# landing page

def landing_page():
    # Hero Section
    st.markdown("""
    <div class="landing-header">
        <h1>🏥 Drug Recommendation System</h1>
        <p>Your Intelligent Medical Companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Grid
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("""<div class="feature-card"><h3>💊<br>Smart Drug Info</h3><p>AI-powered recommendations.</p></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="feature-card"><h3>🤖<br>24/7 AI Chat</h3><p>Chat in any language.</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="feature-card"><h3>🩺<br>Doctor Connect</h3><p>Book appointments instantly.</p></div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Login Section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🚀 Get Started")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("Login", use_container_width=True):
                user, msg = auth.login_user(u, p)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error(msg)
                    
        with tab2:
            nu = st.text_input("New Username", key="s_u")
            np = st.text_input("New Password", type="password", key="s_p")
            role = st.selectbox("Role", ["patient", "doctor"])
            spec = st.selectbox("Specialty", ["General Medicine", "Dermatology", "Psychiatry"]) if role == "doctor" else "General"
            
            if st.button("Sign Up", use_container_width=True):
                success, msg = auth.signup_user(nu, np, role)
                if success:
                    if role == "doctor": doctor_manager.register_doctor_profile(nu, spec)
                    st.success("Account Created! Login now.")
                else:
                    st.error(msg)

# -Main fun
if __name__ == "__main__":
    if st.session_state.user:
        if st.session_state.user['role'] == 'doctor':
            doctor_dashboard()
        elif st.session_state.user['role'] == 'admin':
            admin_dashboard()
        else:
            patient_dashboard()
    else:
        landing_page()