import pandas as pd
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
DATA_FILE = "drugs.csv"
MODELS_DIR = "models"
SVM_PATH = os.path.join(MODELS_DIR, "svm_condition.joblib")
VEC_PATH = os.path.join(MODELS_DIR, "tfidf_condition.joblib")

# Ensure 'models' folder exists
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

# -----------------------------------------------------------------------------
# 1. LOAD DATA
# -----------------------------------------------------------------------------
print("⏳ Loading data...")
try:
    df = pd.read_csv(DATA_FILE)
    # Clean column names
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Fill missing text
    text_cols = ['medical_condition', 'medical_condition_description', 'side_effects']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).fillna("")
            
    print(f"✅ Loaded {len(df)} rows.")
except FileNotFoundError:
    print(f"❌ Error: '{DATA_FILE}' not found. Please check the file name.")
    exit()

# -----------------------------------------------------------------------------
# 2. TRAIN MODEL
# -----------------------------------------------------------------------------
print("🧠 Training SVM Symptom Detector...")

# Combine columns for better learning context
# (Condition Name + Description + Side Effects)
df['training_text'] = df['medical_condition'] + " " + df['medical_condition_description'] + " " + df['side_effects']

X = df['training_text']
y = df['medical_condition'] # The label to predict

# A. Vectorization (Convert text to numbers)
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X_vec = vectorizer.fit_transform(X)

# B. Train SVM
model = LinearSVC(random_state=42, class_weight='balanced')
model.fit(X_vec, y)

print("✅ Model Trained Successfully.")

# -----------------------------------------------------------------------------
# 3. SAVE MODELS
# -----------------------------------------------------------------------------
print(f"💾 Saving models to '{MODELS_DIR}/'...")

joblib.dump(model, SVM_PATH)
joblib.dump(vectorizer, VEC_PATH)

print("🎉 DONE! You can now run 'streamlit run app.py'")