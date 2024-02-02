from langchain_openai import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage, AIMessage
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain

from dotenv import load_dotenv
import os

load_dotenv()
LLM_MODEL = "gpt-3.5-turbo-1106"
DELIMITER = "####"
DISCORD_CHAR_LIMIT = 2000

def get_thread_name(message):
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_KEY"), temperature=1, model=LLM_MODEL, max_tokens=10)
    messages = [
        SystemMessage(
            content=f"""
                You main job is to make names for threads. You will be given questions or comments by the user.
                The user comment or question will be delimited by the following delimiters: ####
                Your job is to make a name for the thread that best summarizes the question or comment.
                Try to make the name as short as possible, but make sure it is descriptive.
                """
        ),
        HumanMessage(content=f"{DELIMITER}{message}{DELIMITER}")
    ]
    return llm.invoke(messages).content

def get_response(prompt, memory):
    # LLM Model
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_KEY"), temperature=0, model=LLM_MODEL, max_tokens=400)
    
    # Prompt Template
    template = """
    Follow the user's instructions carefully. 
    Respond using markdown. DO NOT SHARE ANY CODE AT ANY TIME. Only use words or pseudocode.
    You're a Makecode expert and a high school computer science teacher responding to student questions. 
    Be as brief as possible. Make sure your response does not exceed 2000 characters, including any code examples.
    If the teacher does not know the answer to a question, the teacher truthfully says, "I don't know".
    DO NOT EXCEED 2000 CHARACTERS. 
    The user comment or question will be preceded and proceeded by the following delimiters: ####

    Current conversation:
    {history}
    Student: {input}
    Teacher:"""
    PROMPT = PromptTemplate(input_variables=["history", "input", "delimiter"], template=template)

    # Conversation Chain (Loading Memory)
    conversation = ConversationChain(
        prompt=PROMPT,
        llm=llm,
        memory=memory,
    )
    # Generating Response
    result = conversation.predict(
        input=f"""
            {DELIMITER}{prompt}{DELIMITER}

            Respond using 2000 characters or less. Be brief!
        """
    )

    result = f"{result}\n\n`Note: Discord limits messages to 2000 characters`"

    # Check if the length of the response exceeds Discord's limit
    if len(result) > DISCORD_CHAR_LIMIT:
        # If it does, truncate it to the maximum allowed length
        result = result[:DISCORD_CHAR_LIMIT]
        print(f"Response was truncated to {DISCORD_CHAR_LIMIT} characters.\n", result)

    return result

# if __name__ == "__main__":
#     llm = ChatOpenAI(api_key=os.getenv("OPENAI_KEY"))
#     memory = ConversationSummaryBufferMemory(llm=llm, ai_prefix="Teacher", human_prefix="Student", max_token_limit=1000)
#     print(get_response("How do I make a thread?", memory))
#     print(get_thread_name("How do I make a thread?"))