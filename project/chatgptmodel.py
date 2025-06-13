import openai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")
client = openai.OpenAI(api_key = api_key)


# Specify the model to use
model = "gpt-4o-mini"

def chat_answers_question(prompt_from_area):
    # Prompt the user for input

    user_prompt = prompt_from_area
    if user_prompt:
        # Generate a response using the OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_prompt}
           ],
            #we will integrate something to play with temp and token
            temperature=0.7,
            max_tokens=150
        )

        # Display the generated text
        return "Generated text:\n", response.choices[0].message.content
    else: return "where is the question"

#chat_answers_question("tell a joke")