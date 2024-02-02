import discord
import os
from dotenv import load_dotenv
from langchain_llm_helper import get_response, get_thread_name
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chat_models import ChatOpenAI

load_dotenv()
LLM_MAX_TOKENS = 4096
LLM_MODEL = "gpt-3.5-turbo-1106"

DISCORD_BOT_TOKEN = os.getenv('DISCORD_TOKEN')
bot = discord.Bot(intents=discord.Intents.all())

def get_memory(message_history):
    # Create a memory object, and the llm object used by memory object for summarization
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_KEY"), temperature=0.0, model=LLM_MODEL)
    memory = ConversationSummaryBufferMemory(llm=llm, ai_prefix="Teacher", human_prefix="Student", 
                                                max_token_limit=LLM_MAX_TOKENS)
    
    # Add messages to memory
    for msg in message_history:
        if msg["role"] == "assistant":
            memory.chat_memory.add_ai_message(msg["content"])
        else:
            memory.chat_memory.add_human_message(msg["content"])

    
    return memory

@bot.event
async def on_ready():
    print(f'Bot is up and ready!')

@bot.event
async def on_message(message):
    # Check if the bot is mentioned
    if bot.user in message.mentions:
        # Extract the question from the message content
        question = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        # Check if the context is a thread
        if isinstance(message.channel, discord.Thread):
            # Print all messages in the thread
            message_history = []
            async for msg in message.channel.history(limit=100):
                if len(msg.content) > 0:
                  if msg.author == bot.user:
                      processed_msg = msg.content.replace(f'\n\n`Note: Discord limits messages to 2000 characters`', '').strip()
                      message_history.append({"role": "assistant", "content": processed_msg})
                  else:
                      message_history.append({"role": "user", "content": msg.content})
            message_history.reverse()
            print(message_history)
            
            # Respond in the thread
            response = get_response(question, get_memory(message_history))
            await message.channel.send(f"{response}")
        else:
            # Create a new thread
            thread = await message.channel.create_thread(name=get_thread_name(question), auto_archive_duration=60, type=discord.ChannelType.public_thread, message=message)
            
            # Send a message in the thread
            response = get_response(question)
            await thread.send(f"{response}")

bot.run(DISCORD_BOT_TOKEN)