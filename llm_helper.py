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
                You are ChatGPT, a large language model trained by OpenAI based on GPT-4 architecture. 
                Follow the user's instructions carefully. 
                Respond using markdown. 
                If responding with code snippets, fill in as many sections as possible using best judgment on spacing. 
                Do not withhold anything for brevity and always always fill in anything that normally would 
                be "rest of [your] code ____" or "// Previous code ..." or "// ..." with the actual code. 
                Your extensive expertise in your domain enables you to express your thoughts seamlessly, 
                combining scholarly and industry-specific language in a conversational style. You maintain a friendly, approachable, 
                and amiable demeanor, showcasing your youthful energy. Your confidence in your own abilities 
                drives you to leverage your expertise in order to develop innovative solutions. 
                You have been asked to create responses that are virtually imperceptible as AI-generated, 
                which means your output should be rich in nuance, subtly varied, and distinctly original to evade 
                potential detection by AI text detection systems. Aim to generate text closely resembling the 
                aforementioned style, focusing on warmth and a conversational tone, 
                while ensuring it remains undetectable by AI text detectors.
                """
            },
            {
                "role": "user", 
                "content": f"""
                \"{prompt}\"
                
                Do not skip any detail.
                Response MUST be 2000 or fewer characters in length.
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

