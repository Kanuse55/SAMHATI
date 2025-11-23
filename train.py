import pandas as pd
import os
import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
DATA_FILE = "drugs.csv"
MODELS_DIR = "models"
SVM_PATH = os.path.join(MODELS_DIR, "svm_condition.joblib")
VEC_PATH = os.path.join(MODELS_DIR, "tfidf_condition.joblib")

if not os.path.exists(MODELS_DIR): os.makedirs(MODELS_DIR)

# -----------------------------------------------------------------------------
# 1. LOAD DATA
# -----------------------------------------------------------------------------
print("⏳ Loading data...")
df = pd.read_csv(DATA_FILE)
df.columns = [c.lower().strip() for c in df.columns]

# Clean NaNs
text_cols = ['medical_condition', 'medical_condition_description', 'side_effects']
for col in text_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).fillna("")

# -----------------------------------------------------------------------------
# 2. THE "REALISTIC" FIX (BLINDFOLDING)
# -----------------------------------------------------------------------------
print("\n🙈 Applying 'Blindfold' (Removing disease names from text)...")

def clean_training_text(row):
    # Combine description and side effects
    text = row['medical_condition_description'] + " " + row['side_effects']
    condition = row['medical_condition']
    
    # Remove the condition name from the text (Case Insensitive)
    # e.g. Remove "Acne" from "Acne is a skin disease" -> " is a skin disease"
    if len(condition) > 3: # Only remove if it's a significant word
        text = re.sub(r'\b' + re.escape(condition) + r'\b', '', text, flags=re.IGNORECASE)
    
    return text

# Apply the cleaning
df['training_text'] = df.apply(clean_training_text, axis=1)

X = df['training_text']
y = df['medical_condition']

# -----------------------------------------------------------------------------
# 3. EVALUATE REALISTIC ACCURACY
# -----------------------------------------------------------------------------
print("🧠 Training on sanitized data...")

vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X_vec = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)

model = LinearSVC(random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

preds = model.predict(X_test)
acc = accuracy_score(y_test, preds) * 100

print("-" * 40)
print(f"🎯 REALISTIC ACCURACY: {acc:.2f}%")
print("-" * 40)

# -----------------------------------------------------------------------------
# 4. SAVE
# -----------------------------------------------------------------------------
print("\n💾 Retraining on full realistic data and saving...")
final_model = LinearSVC(random_state=42, class_weight='balanced')
final_model.fit(X_vec, y)

joblib.dump(final_model, SVM_PATH)
joblib.dump(vectorizer, VEC_PATH)

print("✅ Models Saved.")