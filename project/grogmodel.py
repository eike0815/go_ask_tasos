import re
import json
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

model = "llama-3.3-70b-versatile"

def extract_json_block(response_text):
    """
    Extracts the first JSON block from a string using regex.
    """
    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
    except Exception as e:
        print("❌ Grog JSON extraction failed:", e)
    return None

def give_answer(prompt_from_area, system_prompt_override=None, temperature=0.7, max_tokens=150):
    """
    Calls the Grog model and returns a structured JSON response similar to ChatGPT:
    - "answer": the model's answer
    - "confidence": a value between 0 and 1
    """

    user_prompt = f"""
    Please answer the following question and respond ONLY in JSON format with two keys:
    - "answer": your answer to the question
    - "confidence": a number between 0 and 1 showing how confident you are

    Question: {prompt_from_area}
    """

    system_message = system_prompt_override or {
        "role": "system",
        "content": "You are an AI-model that always responds with a JSON object."
    }

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                system_message,
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        response_text = response.choices[0].message.content
        parsed_json = extract_json_block(response_text)

        if parsed_json:
            return "Structured response:", parsed_json
        else:
            return "⚠️ Could not parse structured output", response_text

    except Exception as e:
        return "❌ Grog completion error:", str(e)
