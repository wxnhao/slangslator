import discord
import os
from dotenv import load_dotenv
load_dotenv()

bot = discord.Bot()

# we need to limit the guilds for testing purposes
# so other users wouldn't see the command that we're testing

@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")
    
@bot.command(description="Hello worold") # this decorator makes a slash command
async def hello(ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Hello {ctx.author.mention}")

bot.run(os.getenv('TOKEN'))