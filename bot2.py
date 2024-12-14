import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.hybrid_command(name="hello", description="Say hello!")
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.mention}!')

@bot.hybrid_command(name="add", description="add")
async def add(ctx, num1: int, num2: int):
    await ctx.send(f'The sum is {num1 + num2}')

bot.run(os.getenv('TOKEN'))