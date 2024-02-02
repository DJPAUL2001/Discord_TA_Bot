import discord
import os
from dotenv import load_dotenv
from llm_helper import get_response, get_thread_name

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
bot = discord.Bot(intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f'Bot is up and ready!')

# @bot.slash_command(name='ask', description="Enter your question here.")
# async def ask(ctx: discord.ApplicationContext, question: str):
#     await ctx.defer()
#     response = get_response(question)
#     # Check if the context is a thread
#     if isinstance(ctx.channel, discord.Thread):
#         # Print all messages in the thread
#         async for message in ctx.channel.history(limit=100):
#             print(message.content)
        
#         # Respond in the thread
#         await ctx.respond(f"{ctx.author.name}: `{question}`\n\nResponse: `{response}`\n\nNote: Discord limits messages to 2000 characters")
#     else:
#         # Respond in the thread
#         await ctx.respond(f"Creating new thread...")

#         # Create a new thread
#         thread = await ctx.channel.create_thread(name="Thread name", auto_archive_duration=60, type=discord.ChannelType.public_thread)
        
#         # Send a message in the thread
#         await thread.send(f"{ctx.author.name}: `{question}`\n\nResponse: `{response}`\n\nNote: Discord limits messages to 2000 characters")

@bot.event
async def on_message(message):
    # Check if the bot is mentioned
    if bot.user in message.mentions:
        # Extract the question from the message content
        question = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        # Check if the context is a thread
        if isinstance(message.channel, discord.Thread):
            message_history = []
            # Print all messages in the thread
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
            response = get_response(question, message_history)
            await message.channel.send(f"{response}\n\n`Note: Discord limits messages to 2000 characters`")
        else:
            # Create a new thread
            thread = await message.channel.create_thread(name=get_thread_name(question), auto_archive_duration=60, type=discord.ChannelType.public_thread, message=message)
            
            # Send a message in the thread
            response = get_response(question)
            await thread.send(f"{response}\n\n`Note: Discord limits messages to 2000 characters`")

bot.run(TOKEN)