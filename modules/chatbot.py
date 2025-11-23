from openai import OpenAI
import streamlit as st

ENDPOINT = "https://models.inference.ai.azure.com"
MODEL_NAME = "gpt-4o" 

def _generate_offline_response(recommended_drugs_df):
    """
    Internal Helper: Generates a template response when AI is unavailable.
    Now handles 'General' greetings gracefully.
    """
    if recommended_drugs_df.empty:
        # This handles greetings (Hi, Hello) or unrecognized symptoms in offline mode
        return (
            "👋 **Hello!**\n\n"
            "I am currently in **Offline Mode** (Database Only).\n"
            "I can recommend drugs if you type a symptom like:\n"
            "- *'I have a headache'*\n"
            "- *'Best medicine for acne'*\n\n"
            "*(Please type a medical condition to get started.)*"
        )

    # Extract top drug details
    top_drug = recommended_drugs_df.iloc[0]
    
    return (
        f"**✅ Database Match (Offline Mode):**\n\n"
        f"Based on your symptoms, the system detected: **{top_drug['medical_condition']}**.\n\n"
        f"**Top Recommended Drug:**\n"
        f"💊 **{top_drug['drug_name']}**\n"
        f"⭐ **Rating:** {top_drug['rating']}/10\n"
        f"👥 **Reviews:** {top_drug['no_of_reviews']:.0f} users\n\n"
        f"⚠️ **Side Effects:** {str(top_drug['side_effects'])[:120]}...\n\n"
        f"*(Note: AI Chat is currently offline. Showing direct database results.)*"
    )

def get_ai_response(api_key, user_input, recommended_drugs_df, chat_history):
    """
    Main Logic: Tries to use GPT-4o. If token is missing or API fails, falls back to Offline Template.
    """
    
    # 1. CHECK TOKEN: If invalid/placeholder, skip straight to offline mode
    if not api_key or "PASTE" in api_key or len(api_key) < 10:
        return _generate_offline_response(recommended_drugs_df)

    # 2. PREPARE ONLINE CONTEXT
    client = OpenAI(base_url=ENDPOINT, api_key=api_key)

    system_instruction = """
    You are PharmaConnect, a helpful medical assistant.
    RULES:
    1. Answer ONLY health/drug related questions. Refuse off-topic queries politely.
    2. Context provided below contains the BEST drugs for the user's condition based on ratings.
    3. Recommend these drugs explicitly and explain why they are good based on the data provided.
    4. Keep the tone empathetic and professional.
    """

    if not recommended_drugs_df.empty:
        top_drugs = recommended_drugs_df.head(3)
        drugs_str = ""
        for _, row in top_drugs.iterrows():
            drugs_str += f"- {row['drug_name']} (Rating: {row['rating']}/10, Reviews: {row['no_of_reviews']})\n"
        
        context_text = f"{system_instruction}\n\nCONTEXT: The user has a condition matching these top-rated drugs:\n{drugs_str}"
    else:
        # If no drugs found (or it was a greeting), give general advice/greeting
        context_text = f"{system_instruction}\n\nINSTRUCTION: No specific drugs found in database. If the user said 'Hi/Hello', greet them warmly and ask for their symptoms. If it was a medical query, provide general advice and suggest a doctor."

    messages = [{"role": "system", "content": context_text}]
    messages.extend(chat_history[-4:]) # Keep last 4 messages for context
    messages.append({"role": "user", "content": user_input})

    # 3. ATTEMPT API CALL
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.6,
        )
        return response.choices[0].message.content

    except Exception as e:
        # 4. FALLBACK: If API fails (Network error, Quota exceeded, or Bad Token), use Offline Mode
        print(f"⚠️ API Error (Falling back to offline): {e}")
        return _generate_offline_response(recommended_drugs_df)