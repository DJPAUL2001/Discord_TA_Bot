import discord
import os
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from llm_helper import get_response

load_dotenv()

TOKEN = os.getenv("TOKEN")
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
  print("Bot is up and ready!")
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)

"""
Note: When you set ephemeral=True in a response, the message will be sent as an ephemeral message. 
Only the user who triggered the command will be able to see this message. 
Other users in the channel will not be able to see it.
"""
# @bot.tree.command(name="hello")
# async def hello(interaction: discord.Interaction):
#   await interaction.response.send_message(f'Hey {interaction.user.mention}! This is a slash command!', ephemeral=True)

@bot.tree.command(name="ask")
@app_commands.describe(question="Enter your question here.")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    response = get_response(question)
    await interaction.followup.send(f"{interaction.user.name} asked: `{question}`\n\nResponse: {response}")

bot.run(TOKEN)