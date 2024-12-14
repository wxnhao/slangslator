import openai
import os
from dotenv import load_dotenv
load_dotenv()

# API key 
openai.api_key = os.getenv("TOKEN")

#take in a text and key.
def generate_explanation(message_txt, language, response_amount, max_tokens=800):

    #set up the prompt with the message (Change this to newer prompt)
    explaination_prompt = f"Using the language: '{language}' Explain the slangs in following text: '{message_txt}'"

    #get the response
    explaination_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": explaination_prompt}
        ],
        n=response_amount,
        max_tokens=max_tokens,
        temperature=1,
    )
    #choose the explaination content and store it
    explainations = []
    for x in range(response_amount):
        explainations.append(explaination_response.choices[x].message.content)

    #return the explainations
    return explainations

print(generate_explanation("meow nya uwu :3", "ENGLISH", 3, max_tokens=800))
