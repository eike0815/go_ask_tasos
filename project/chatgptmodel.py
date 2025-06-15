import openai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")
client = openai.OpenAI(api_key=api_key)

model = "gpt-4o-mini"

def chat_answers_question(prompt_from_area, system_prompt_override=None, temperature=0.7, max_tokens=150):
    user_prompt = prompt_from_area

    if user_prompt:
        system_message = system_prompt_override or {
            "role": "system",
            "content": "You are a helpful assistant."
        }

        response = client.chat.completions.create(
            model=model,
            messages=[
                system_message,
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return "Generated text:\n", response.choices[0].message.content
    else:
        return "where is the question"