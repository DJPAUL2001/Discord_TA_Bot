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

@bot.tree.command(name="Hello")
async def hello(interaction: discord.Interaction):
  await interaction.response.send_message(f'Hey {interaction.user.mention}! This is a slash command!', ephemeral=True)

@bot.tree.command(name="Ask Question")
@app_commands.describe(thing_to_say = "Ask your question here.")
async def say(interaction: discord.Interaction, thing_to_say: str):
  await interaction.response.send_message(f"""
      {interaction.user.name} said: `{thing_to_say}`;
      I said: `{get_response(thing_to_say)}`
  """)

bot.run(TOKEN)