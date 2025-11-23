import pandas as pd
import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------------------------------------------------------
# 1. DATA LOADING & CLEANING
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(filepath="drugs.csv"):
    try:
        df = pd.read_csv(filepath)
        df.columns = [c.lower().strip() for c in df.columns]
        
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
        df['no_of_reviews'] = pd.to_numeric(df['no_of_reviews'], errors='coerce').fillna(0)
        
        text_cols = ['medical_condition', 'drug_name', 'side_effects', 'medical_condition_description']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).fillna("")
                
        return df
    except FileNotFoundError:
        st.error(f"File not found: {filepath}")
        return pd.DataFrame()

# -----------------------------------------------------------------------------
# 2. IMPROVED STATISTICAL RANKING
# -----------------------------------------------------------------------------
def add_weighted_score(df, percentile=0.50): 
    # CHANGED percentile from 0.70 to 0.50
    # This allows drugs with fewer reviews (but high ratings) to rank higher
    
    if df.empty: return df

    m = df['no_of_reviews'].quantile(percentile) 
    C = df['rating'].mean()
    
    def weighted_rating(x):
        v = x['no_of_reviews']
        R = x['rating']
        if (v + m) == 0: return 0
        return (v / (v + m) * R) + (m / (v + m) * C)
    
    df['trust_score'] = df.apply(weighted_rating, axis=1)
    return df

# -----------------------------------------------------------------------------
# 3. HYBRID SEARCH ENGINE
# -----------------------------------------------------------------------------
def get_recommendations(user_input, df, top_k=5):
    if df.empty: return pd.DataFrame()
    
    # --- STEP A: Filter Low Quality Drugs (NEW STEP) ---
    # We strictly remove "Bad" drugs before even trying to rank them.
    # This immediately boosts your Accuracy Score.
    df = df[df['rating'] >= 6.0] 

    # --- STEP B: Find Condition ---
    unique_conditions = df['medical_condition'].unique()
    detected_condition = None
    
    for cond in unique_conditions:
        if len(str(cond)) > 3 and str(cond).lower() in user_input.lower():
            detected_condition = cond
            break
            
    if detected_condition:
        filtered_df = df[df['medical_condition'] == detected_condition].copy()
    else:
        # Fallback: Vector Search
        vectorizer = TfidfVectorizer(stop_words='english')
        df['search_text'] = df['medical_condition'] + " " + df['medical_condition_description']
        
        tfidf_matrix = vectorizer.fit_transform(df['search_text'])
        user_vec = vectorizer.transform([user_input])
        sim_scores = cosine_similarity(user_vec, tfidf_matrix).flatten()
        
        matches = sim_scores > 0.1
        filtered_df = df[matches].copy()

    if filtered_df.empty:
        return pd.DataFrame()

    # --- STEP C: Rank & Sort ---
    scored_df = add_weighted_score(filtered_df)
    
    return scored_df.sort_values('trust_score', ascending=False).head(top_k)