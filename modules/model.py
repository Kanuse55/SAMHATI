import pandas as pd
import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------------------------------------------------------
# 1. DATA LOADING & CLEANING (With Caching)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(filepath="drugs.csv"):
    """
    Loads dataset, standardizes columns, and fills missing values.
    """
    try:
        df = pd.read_csv(filepath)
        
        # Clean column names (lowercase, strip spaces)
        df.columns = [c.lower().strip() for c in df.columns]
        
        # Convert numeric columns (handle errors)
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
        df['no_of_reviews'] = pd.to_numeric(df['no_of_reviews'], errors='coerce').fillna(0)
        
        # Fill text NaNs
        text_cols = ['medical_condition', 'drug_name', 'side_effects', 'medical_condition_description']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).fillna("")
                
        return df
    except FileNotFoundError:
        st.error(f"File not found: {filepath}. Please ensure drugs.csv is in the project folder.")
        return pd.DataFrame()

# -----------------------------------------------------------------------------
# 2. STATISTICAL RANKING (The Weighted Formula)
# -----------------------------------------------------------------------------
def add_weighted_score(df, percentile=0.70):
    """
    Calculates Trust Score based on Rating + Review Count.
    """
    if df.empty: return df

    m = df['no_of_reviews'].quantile(percentile) # Minimum reviews required
    C = df['rating'].mean()                      # Average rating of the whole set
    
    def weighted_rating(x):
        v = x['no_of_reviews']
        R = x['rating']
        if (v + m) == 0: return 0
        return (v / (v + m) * R) + (m / (v + m) * C)
    
    df['trust_score'] = df.apply(weighted_rating, axis=1)
    return df

# -----------------------------------------------------------------------------
# 3. HYBRID SEARCH ENGINE (NLP + Ranking)
# -----------------------------------------------------------------------------
def get_recommendations(user_input, df, top_k=5):
    """
    Finds drugs based on user input and sorts by Trust Score.
    """
    if df.empty: return pd.DataFrame()
    
    # A. Keyword Search (Fastest)
    # Check if any known condition exists in the user input
    unique_conditions = df['medical_condition'].unique()
    detected_condition = None
    
    for cond in unique_conditions:
        if len(str(cond)) > 3 and str(cond).lower() in user_input.lower():
            detected_condition = cond
            break
            
    if detected_condition:
        # Filter exactly for this condition
        filtered_df = df[df['medical_condition'] == detected_condition].copy()
    else:
        # B. Fallback: TF-IDF Vectorization (Smart Search)
        # If user describes symptoms ("my head hurts") instead of condition ("Headache")
        vectorizer = TfidfVectorizer(stop_words='english')
        
        # Create a search pool: Condition + Description
        df['search_text'] = df['medical_condition'] + " " + df['medical_condition_description']
        
        tfidf_matrix = vectorizer.fit_transform(df['search_text'])
        user_vec = vectorizer.transform([user_input])
        
        # Calculate similarity
        sim_scores = cosine_similarity(user_vec, tfidf_matrix).flatten()
        
        # Filter rows with > 0.1 similarity
        matches = sim_scores > 0.1
        filtered_df = df[matches].copy()

    if filtered_df.empty:
        return pd.DataFrame()

    # C. Apply Ranking & Sort
    scored_df = add_weighted_score(filtered_df)
    
    # Return top results
    return scored_df.sort_values('trust_score', ascending=False).head(top_k)