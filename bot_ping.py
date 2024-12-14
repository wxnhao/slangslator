import discord
import os
from example_modal import  MyModal
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

@bot.command(description="Send a modal to the user")
async def modal(ctx):
    modal = MyModal(title="Modal via Slash Command")
    await ctx.send_modal(modal)

@bot.command(description="Translate a message")
@discord.option("messageId", type=discord.SlashCommandOptionType.string)
async def translate(ctx, messageId: str):
    await ctx.respond(f"messageId = {messageId}", True)

bot.run(os.getenv('TOKEN'))