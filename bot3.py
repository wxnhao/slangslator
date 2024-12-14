import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()

# Intents and bot setup
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Slash command: /hello
@bot.tree.command(name="hello", description="Say hello!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.name}!")

# Syncing commands to the guild
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    try:
        # Replace with your Guild ID for faster command testing
        guild = discord.Object(id=1317567857764077568)
        await bot.tree.sync(guild=guild)
        print("Slash commands synced successfully!")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Run the bot
bot.run(os.getenv('TOKEN'))
