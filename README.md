Install Dependencies Ensure you have Python installed, then run:

Bash

pip install -r requirements.txt


Set Up API Token:

Open app.py.

Locate the line: GITHUB_TOKEN = "token"

Replace "token" with your actual GitHub Models API Key.

Run the Application

Bash

streamlit run app.py

🏥 PharmaConnect AI
PharmaConnect AI is an intelligent healthcare platform that bridges the gap between patients, medical information, and doctors. It utilizes a Hybrid Recommendation Engine (NLP + Statistical Ranking) to suggest the best drugs based on real-world reviews and integrates a full Doctor Consultation System.

🚀 Key Features
👤 For Patients
AI Health Assistant: A multilingual chatbot (powered by GPT-4o) that understands symptoms in natural language (e.g., "Pet dukh raha hai" or "I have acne") and suggests treatments.

Smart Drug Recommendations: Uses a Weighted Trust Score algorithm (similar to IMDB ratings) to rank drugs based on effectiveness and user reviews.

Visual Analytics: Interactive graphs showing the "Popularity vs. Rating" landscape of recommended drugs.

Doctor Consultation: Search for specialists based on medical condition and book appointments instantly.

👨‍⚕️ For Doctors
Professional Dashboard: View and manage incoming appointment requests.

Status Control: Toggle availability ("Available" / "Busy") in real-time.

Appointment Actions: Accept or Reject patient requests with a single click.

🛡️ For Admins
System Monitoring: Track total users, doctors, drugs, and reviews.

Data Inspection: View raw data tables for Users, Doctors, and the Drug Database.

User Analytics: Visual distribution of user roles.

🛠️ Tech Stack
Frontend: Streamlit (Python) with Custom CSS (Teal/Medical Theme).

AI & NLP: OpenAI GPT-4o (via GitHub Models) for symptom extraction and conversational responses.

Data Processing: Pandas & NumPy.

Visualization: Plotly Express.

Authentication: BCrypt for secure password hashing.

Database: CSV-based lightweight persistence (users.csv, doctors.csv, appointments.csv).


