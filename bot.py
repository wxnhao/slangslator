import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()

class SlangslatorBot(commands.Bot):
    def __init__(self):
        super().__init__(
            '',
            intents=discord.Intents.default(),
            status=discord.Status.do_not_disturb,
            activity=discord.Activity(name='/translate',type=2),
        )
        self.synced = False

    async def setup_hook(self):
        self.add_command(self.hello)

    async def on_ready(self):
        if not self.synced:
            await self.tree.sync()
            self.synced = True
        print(f'[Slangslator] :: Logged in as {self.user}')
    
    # What decorate do I add here to use a command?
    @commands.command(name='hello')
    async def hello(self, ctx):
        await ctx.send(f'Hello, {ctx.author.mention}!')

TOKEN = os.getenv('TOKEN')
bot = SlangslatorBot()
bot.run(TOKEN)

