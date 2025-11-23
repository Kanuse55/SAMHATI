import pandas as pd
import numpy as np
import streamlit as st

# -----------------------------------------------------------------------------
# 1. DATA LOADING
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(filepath="drugs.csv"):
    try:
        df = pd.read_csv(filepath)
        df.columns = [c.lower().strip() for c in df.columns]
        
        # Clean numeric
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
        df['no_of_reviews'] = pd.to_numeric(df['no_of_reviews'], errors='coerce').fillna(0)
        
        # Clean text
        text_cols = ['medical_condition', 'drug_name', 'side_effects']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).fillna("")
                
        return df
    except FileNotFoundError:
        st.error(f"File not found: {filepath}")
        return pd.DataFrame()

# -----------------------------------------------------------------------------
# 2. STATISTICAL RANKING LOGIC
# -----------------------------------------------------------------------------
def get_recommendations(condition, df, top_k=5):
    """
    Input: Exact Condition Name (from SVM)
    Output: Top Rated Drugs
    """
    if df.empty: return pd.DataFrame()
    
    # 1. Filter by Condition (Exact Match or Partial)
    # We use string contains to be safe (e.g. "Acne" matches "Acne (Severe)")
    subset = df[df['medical_condition'].str.contains(condition, case=False, na=False)].copy()
    
    if subset.empty: return pd.DataFrame()

    # 2. Quality Filter (Remove Bad Drugs)
    subset = subset[subset['rating'] >= 6.0]
    
    if subset.empty: return pd.DataFrame()

    # 3. Weighted Ranking Formula (IMDB Score)
    m = subset['no_of_reviews'].quantile(0.50)
    C = subset['rating'].mean()
    
    def weighted_rating(x):
        v = x['no_of_reviews']
        R = x['rating']
        if (v+m) == 0: return 0
        return (v/(v+m) * R) + (m/(v+m) * C)
    
    subset['trust_score'] = subset.apply(weighted_rating, axis=1)
    
    return subset.sort_values('trust_score', ascending=False).head(top_k)