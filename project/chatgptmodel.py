import openai
from dotenv import load_dotenv
import os
import re
import json

load_dotenv()
api_key = os.getenv("API_KEY")
client = openai.OpenAI(api_key=api_key)

model = "gpt-4o-mini"

def extract_json_block(response_text):
    """
    Extracts the first JSON block from a string using regex.
    Returns a Python dict if successful, else None.
    """
    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
        else:
            raise ValueError("No JSON block found")
    except Exception as e:
        print("❌ Failed to extract JSON:", e)
        return None

def chat_answers_question(prompt_from_area, system_prompt_override=None, temperature=0.7, max_tokens=150):
    """
    Calls the GPT model and returns a structured JSON response containing 'answer' and 'confidence'.
    If the model returns extra text, it tries to extract and parse the JSON block.
    """
    user_prompt = f"""
    Please answer the following question and respond in JSON format with two keys:
    - "answer": your main answer
    - "confidence": a number between 0 and 1 indicating your confidence

    Question: {prompt_from_area}
    """

    system_message = system_prompt_override or {
        "role": "system",
        "content": "You are a helpful assistant that always responds with a JSON object."
    }

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                system_message,
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        response_text = response.choices[0].message.content
        parsed_json = extract_json_block(response_text)

        if parsed_json:
            return "Structured response:", parsed_json
        else:
            return "⚠️ Could not parse structured output", response_text

    except Exception as e:
        return "❌ Error during completion:", str(e)
