import openai
import os
from dotenv import load_dotenv
load_dotenv()

# API key (IDK PUT A KEY HERE LOL)
openai.api_key = os.getenv("TOKEN")

#take in a text and key.
def generate_explanation(message_txt, language, max_tokens=800):

    #set up the prompt with the message
    explaination_prompt = f"Using the language: '{language}' Explain the slangs in following text: '{message_txt}'"

    #get the response
    explaination_response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": explaination_prompt}
        ],
        max_tokens=max_tokens,
        temperature=1,
    )
    #choose the first/best explaination content and store it
    explaination = explaination_response.choices[0].message.content

    #return the explaination
    return explaination

print(generate_explanation("THIS IS FIRE", "ENGLISH", max_tokens=800))
