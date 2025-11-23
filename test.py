import pandas as pd
import numpy as np
from modules import model

# 1. Load Data
df = model.load_data()
print(f"Loaded Dataset: {len(df)} rows")

# 2. Configuration
# We define a "Correct Recommendation" as a drug with a Rating > 8.0
# We defines a "Bad Recommendation" as a drug with a Rating < 6.0
RATING_THRESHOLD = 8.0 
TOP_K = 3  # We check the top 3 suggestions for every condition

# 3. Get all unique conditions in the database
all_conditions = df['medical_condition'].unique()
print(f"Testing System across {len(all_conditions)} unique medical conditions...\n")

total_recommendations = 0
successful_recommendations = 0

# 4. The Loop (Simulate a user asking about EVERY condition)
for condition in all_conditions:
    # Get Top 3 Recommendations using your model logic
    recs = model.get_recommendations(condition, df, top_k=TOP_K)
    
    if not recs.empty:
        for _, row in recs.iterrows():
            total_recommendations += 1
            
            # Check if the recommended drug meets the quality standard
            if row['rating'] >= RATING_THRESHOLD:
                successful_recommendations += 1

# 5. Calculate Final Score
if total_recommendations > 0:
    accuracy_score = (successful_recommendations / total_recommendations) * 100
else:
    accuracy_score = 0

# 6. Print Report
print("="*50)
print("🎯 SYSTEM ACCURACY REPORT")
print("="*50)
print(f"Total Conditions Tested:   {len(all_conditions)}")
print(f"Total Drugs Recommended:   {total_recommendations}")
print(f"High Quality Recs (>8.0):  {successful_recommendations}")
print("-" * 30)
print(f"✅ SYSTEM RELIABILITY SCORE: {accuracy_score:.2f}%")
print("="*50)

# Explanation for your presentation
print("\n📝 NOTE FOR PROJECT REPORT:")
print(f"This metric (Precision@{TOP_K}) indicates that {accuracy_score:.1f}% of the time,")
print("the top 3 drugs recommended by the AI have a user rating of 8.0/10 or higher.")