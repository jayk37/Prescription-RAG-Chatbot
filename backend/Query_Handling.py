
from openai import AzureOpenAI, OpenAI
import re

import os
from groq import Groq

# Assuming you've already defined the OpenAI client and model as in your given code:
# api_res = {
#     "base_url": "http://localhost:1234/v1",
#     "api_key": "lm-studio"
# }

# client = OpenAI(**api_res)
# model = "llama-3.2-3b-instruct"

client = Groq(
    api_key="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",
)
model = "llama-3.2-3b-preview"
# Function to interact with the local LLM
def generate(prompt, context=None, instruction=None):
    if context:
        context = f"context : {context}\n"
    else:
        context = ""
    if instruction:
        instruction = f"{instruction}\n"
    else:
        instruction = "base on the prompt give output"
    
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"{context}"},
            {"role": "user", "content": f"prompt : {prompt}"}
        ],
        temperature=0.7,
    )
    
    res = completion.choices[0].message.content
    return res

# Define an agent function that extracts the drug name
def extract_drug_name(user_input):
    if not user_input.strip():
        print("No drug name provided. Waiting for user input...")
        return []
    # Defining a prompt that instructs the LLM to extract only the drug name
    prompt = f"Extract the drug name from the following query: '{user_input}. Just output the drug name. No other filler sentences or anything. Only the drug name'"
    
    # Generate a response from the LLM
    drug_name = generate(prompt)
    print("The drug name is: ",drug_name)

    return drug_name


