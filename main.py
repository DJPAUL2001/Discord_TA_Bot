import discord
import os
from dotenv import load_dotenv
from langchain_llm_helper import get_response, get_thread_name, get_memory

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_TOKEN')
bot = discord.Bot(intents=discord.Intents.all())

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
            response = get_response(question, get_memory())
            await thread.send(f"{response}")

bot.run(DISCORD_BOT_TOKEN)