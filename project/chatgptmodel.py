import openai
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("API_KEY")
client = openai.OpenAI(api_key=api_key)

model = "gpt-4o-mini"

# JSON-Schema für forced structured output
schema = {
    "name": "answer_schema",
    "type": "object",
    "strict": True,
    "properties": {
        "answer": {"type": "string"},
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        }
    },
    "required": ["answer", "confidence"],
    "additionalProperties": False
}

def chat_answers_question(prompt_from_area, system_prompt_override=None, temperature=0.7, max_tokens=150):
    """
    Calls the GPT model and returns a structured JSON response with 'answer' and 'confidence',
    enforced via OpenAI's structured output (response_format: json_schema).
    """
    system_message = system_prompt_override or {
        "role": "system",
        "content": "You are a helpful assistant. Always respond using the required JSON structure."
    }

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                system_message,
                {"role": "user", "content": prompt_from_area}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "schema": schema,
                    "name": "answer_schema"
                }
            }
        )

        response_json = response.choices[0].message.content
        parsed_json = json.loads(response_json)

        return "✅ Structured response:", parsed_json

    except Exception as e:
        return "❌ Error during completion:", str(e)
