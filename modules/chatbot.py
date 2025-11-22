from openai import OpenAI
import streamlit as st

ENDPOINT = "https://models.inference.ai.azure.com"
MODEL_NAME = "gpt-4o" 

def extract_condition_with_ai(api_key, user_input):
    """
    Strictly extracts medical conditions. 
    If input is "Hi", "Hello", "How are you", returns 'General'.
    """
    client = OpenAI(base_url=ENDPOINT, api_key=api_key)
    
    system_prompt = """
    You are a medical entity extractor. 
    your task is to extract meadical codition from user input. if he ask you to do something else return a message saying ask health related questions.
    1. If the user input is a greeting (Hi, Hello), a general question, or gibberish, return 'General'.
    2. If the user mentions a symptom or condition (e.g., 'Pet dard', 'Acne', 'Fever'), extract the medical name in English.
    3. Return ONLY the condition name or 'General'. Do not add punctuation.

    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "General"

def get_ai_response(api_key, user_input, recommended_drugs_df, chat_history):
    client = OpenAI(base_url=ENDPOINT, api_key=api_key)

    # --- STRICT SYSTEM PROMPT ---
    system_instruction = """
    You are PharmaConnect, a strict medical assistant.
    RULES:
    1. You MUST ONLY answer questions related to Health, Medicine, Drugs, Symptoms, or Biology.
    2. If the user asks about coding, history, politics, writing essays, or general chit-chat (other than greetings), you MUST REPLY: "I apologize, but I am a medical AI. I can only assist you with health-related queries."
    3. Keep answers professional, empathetic, and concise.
    """

    # --- RAG Context ---
    if not recommended_drugs_df.empty:
        top_drugs = recommended_drugs_df.head(3)
        drugs_str = ""
        for _, row in top_drugs.iterrows():
            drugs_str += f"- {row['drug_name']} (Rating: {row['rating']}/10)\n"
        
        context_text = f"{system_instruction}\n\nCONTEXT: The user has a condition matching these drugs in our database:\n{drugs_str}\nINSTRUCTION: Recommend these drugs and explain why. Translate response to user's language."
    else:
        context_text = f"{system_instruction}\n\nINSTRUCTION: No specific database match. Provide general medical guidance for the symptoms described. Advise consulting a doctor."

    messages = [{"role": "system", "content": context_text}]
    messages.extend(chat_history[-4:])
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.5, # Lower temperature = Less creative/hallucinations
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"