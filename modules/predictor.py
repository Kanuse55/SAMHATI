import joblib
import os
import streamlit as st
import re

# Paths
MODEL_DIR = "models"
SVM_PATH = os.path.join(MODEL_DIR, "svm_condition.joblib")
VEC_PATH = os.path.join(MODEL_DIR, "tfidf_condition.joblib")

_svm_model = None
_vectorizer = None

def load_models():
    global _svm_model, _vectorizer
    if _svm_model is None:
        try:
            if not os.path.exists(SVM_PATH): return False
            _svm_model = joblib.load(SVM_PATH)
            _vectorizer = joblib.load(VEC_PATH)
            return True
        except Exception:
            return False
    return True

def predict_condition(user_text):
    """
    1. Smartly filters out greetings (slang, typos, repeats).
    2. Predicts medical condition using SVM.
    """
    text = user_text.lower().strip()
    
    # --- 1. SMART GREETING GUARD ---
    # We use regex patterns to catch variations like "hiii", "hlo", "hy"
    greeting_patterns = [
        r"\bh+[ei]+y*\b",              # Matches: hi, hii, hey, heyy, hy, hie
        r"\bh+e*l+o+\b",               # Matches: hello, helo, hlo, helllo
        r"\bgreetings\b",              # Matches: greetings
        r"\bsup\b",                    # Matches: sup
        r"\b(good\s+)?(morning|afternoon|evening|night)\b", # Matches: good morning, morning
        r"\bhow\s+are\s+you\b",        # Matches: how are you
        r"\bwho\s+are\s+you\b"         # Matches: who are you
    ]
    
    # Check if any pattern matches
    for pattern in greeting_patterns:
        if re.search(pattern, text):
            return "General"

    # --- 2. ML PREDICTION ---
    if not load_models():
        return "General"
    
    try:
        # Vectorize text
        input_vec = _vectorizer.transform([user_text])
        
        # Predict
        prediction = _svm_model.predict(input_vec)[0]
        return prediction
    except Exception:
        return "General"