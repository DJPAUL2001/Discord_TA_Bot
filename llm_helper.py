from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
MAX_TOKENS = 16384  # 4096*4+1


def get_response(prompt, message_history=[]):
    messages = [
        {
            "role": "system",
            "content": """
                Follow the user's instructions carefully. 
                Respond using markdown. DO NOT SHARE ANY CODE AT ANY TIME. Only use words or pseudocode.
                You're a high school computer science teacher responding to student questions. Be as brief as possible.
                Make sure your response does not exceed 2000 characters, including any code examples.
                DO NOT EXCEED 2000 CHARACTERS.
                """,
        },
    ]
    messages.extend(message_history)
    messages.append(
        {
            "role": "user",
            "content": f"""
                \"{prompt}\"
                
                Respond using 2000 characters or less. Be brief!
                """,
        }
    )
    total_tokens = sum([len(message["content"]) for message in messages])
    while total_tokens > MAX_TOKENS:
        # Remove the oldest message
        removed_message = messages.pop(1)
        # Subtract its token count from the total
        total_tokens -= len(removed_message["content"])

    chat_completion = client.chat.completions.create(
        messages=messages,
        # model="gpt-4-1106-preview",
        model="gpt-3.5-turbo-1106",  # for faster response time
        temperature=1,
        top_p=1,
        presence_penalty=0,
        frequency_penalty=0,
        max_tokens=400,  # 4096 is model limit, but 2000 char is discord limit
    )

    result = chat_completion.choices[0].message.content

    # Check if the length of the response exceeds Discord's limit
    if len(result) > 1950:
        # If it does, truncate it to the maximum allowed length
        result = result[:1950]
        print("Response was truncated to 1950 characters.")
        print(result)

    return result
