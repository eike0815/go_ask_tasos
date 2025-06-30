import json
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables and initialize Groq client
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

model = "llama-3.3-70b-versatile"

def give_answer(prompt_from_area, system_prompt_override=None, temperature=0.7, max_tokens=150):
    """
    Sends a question to the Groq LLaMA model and enforces a structured JSON response
    with the following format:
      {
        "answer": "string",
        "confidence": float (between 0 and 1)
      }

    Returns:
        - A status string
        - A parsed dictionary (if successful) or raw error message
    """

    # Use custom system prompt if provided, otherwise fallback to default
    system_message = system_prompt_override or {
        "role": "system",
        "content": (
            "You are an AI model that always responds with a valid JSON object in the following format:\n"
            "{\n"
            "  \"answer\": \"string\",\n"
            "  \"confidence\": number (between 0 and 1)\n"
            "}\n"
            "Do not include any explanation or extra text outside the JSON."
        )
    }

    # ✅ Ensure the word "json" is included to satisfy Groq API requirements
    if "json" not in system_message["content"].lower():
        system_message["content"] += "\n\nNote: Always respond with a valid JSON object."

    # User message containing the actual question
    user_prompt = f"Question: {prompt_from_area}"

    try:
        # Call the Groq API with enforced JSON output
        response = client.chat.completions.create(
            model=model,
            messages=[
                system_message,
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}  # Enforce structured JSON response
        )

        # Read the model's response content
        response_text = response.choices[0].message.content
        print("🔍 Raw output from Groq:", repr(response_text))  # Debug output

        # Parse the JSON string to a Python dictionary
        parsed_json = json.loads(response_text)

        return "Structured response:", parsed_json

    except Exception as e:
        return "❌ Grog completion error:", str(e)
