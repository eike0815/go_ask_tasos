from groq import Groq
from dotenv import load_dotenv
import os
from project.models import Chat, User
from project import main

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
# Initialize the Groq client
client = Groq(api_key=api_key)


# Specify the model to use
model = "llama-3.3-70b-versatile"

# System's task here we integrate what role "tasos" has maybe radio?
system_prompt = "You are an AI-model."

# User's request
def give_answer(prompt_from_area, system_prompt_override=None, temperature=0.7, max_tokens=150):
    user_prompt = f"""here some prompting {prompt_from_area}"""

    system_message = system_prompt_override or {
        "role": "system",
        "content": "You are an AI-model."
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