import discord

class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Short Input"))
        self.add_item(discord.ui.InputText(label="Long Input", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        # embed = discord.Embed(title="Modal Results")
        # embed.add_field(name="Short Input", value=self.children[0].value)
        # embed.add_field(name="Long Input", value=self.children[1].value)
        view = MyView(short=self.children[0].value, long=self.children[1].value)
        view.message = await interaction.response.send_message(embed=view.embed, view=view)

class MyView(discord.ui.View):
    def __init__(self, *, short: str, long: str):
        super().__init__()

        self.short = short
        self.long = long

        self.i = 0
        self.n = 5

        self.reset_embed()
        
        self.prev_button = discord.ui.Button(emoji='<:left:940157746723061810>')
        self.next_button = discord.ui.Button(emoji='<:right:940157728083570748>')
        self.prev_button.callback = self.prev_callback
        self.next_button.callback = self.next_callback

        self.add_item(self.prev_button)
        self.add_item(self.next_button)
    
    def reset_embed(self):
        self.embed = discord.Embed(color=0xff9c2c)
        self.embed.title = self.short+f' {self.i=}'
        self.embed.description = self.long
        # self.embed.set_image()

    async def change_index(self, interaction, i):
        self.i = i%self.n
        self.reset_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)

    async def prev_callback(self, interaction):
        print('prev')
        await self.change_index(interaction, self.i-1)
    
    async def next_callback(self, interaction):
        print('next')
        await self.change_index(interaction, self.i+1)

