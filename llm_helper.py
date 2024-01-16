from tqdm import tqdm
from IPython.display import display, Markdown
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

def get_response(prompt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system", 
                "content":
                """
                Follow the user's instructions carefully. 
                Respond using markdown. DO NOT RESPOND IN CODE.
                Your extensive expertise in your domain enables you to express your thoughts seamlessly, 
                combining scholarly and industry-specific language in a conversational style.
                You maintain a friendly, approachable, and amiable demeanor, showcasing your youthful energy.
                Make sure your response does not exceed 2000 characters, including any code examples.
                DO NOT EXCEED 2000 CHARACTERS.
                """
            },
            {
                "role": "user", 
                "content": f"""
                \"{prompt}\"
                
                Respond using 2000 characters or less. Be brief!
                """
            }
        ],
        # model="gpt-4-1106-preview",
        model="gpt-3.5-turbo-1106",  # for faster response time
        temperature=1,
        top_p=1,
        presence_penalty=0,
        frequency_penalty=0,
        max_tokens=100,  # 4096 is model limit, but 2000 char is discord limit
    )

    result = chat_completion.choices[0].message.content
    # return display(Markdown(result))  # uncomment this line if you are using Jupyter Notebook

    # Check if the length of the response exceeds Discord's limit
    if len(result) > 2000:
        # If it does, truncate it to the maximum allowed length
        result = result[:2000]
        print("Response was truncated to 2000 characters.")
        print(result)

    return result

