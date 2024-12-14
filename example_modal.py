import discord
from copy import deepcopy

class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(
            label="Target",
            placeholder='Enter translation query/slang',
            max_length=50,
        ))
        self.add_item(discord.ui.InputText(
            label="Additional context",
            placeholder="Enter surrounding text as context for higher translation accuracy",
            style=discord.InputTextStyle.long,
            max_length=500,
            required=False
        ))

    async def callback(self, interaction: discord.Interaction):
        # embed = discord.Embed(title="Modal Results")
        # embed.add_field(name="Short Input", value=self.children[0].value)
        # embed.add_field(name="Long Input", value=self.children[1].value)
        target = self.children[0].value
        additional_context = self.children[1].value

        translations = [
            {
                'target': target,
                'additional_context': additional_context,
                'translation': 'ni hao ma',
                'explanation': 'Yada yada explanation exoplanation',
            },
            {
                'target': target,
                'additional_context': additional_context,
                'translation': 'pien',
                'explanation': 'a wejo iasjdfl kasdjflk j',
            },
        ]
        view = MyView(translations)
        view.message = await interaction.response.send_message(embed=view.embed, view=view)

class MyView(discord.ui.View):
    def __init__(self, translations: dict[dict]):
        super().__init__()

        self.translations = deepcopy(translations)

        self.i = 0
        self.n = len(self.translations)

        self.reset_embed()
        
        self.prev_button = discord.ui.Button(emoji='<:left:940157746723061810>')
        self.next_button = discord.ui.Button(emoji='<:right:940157728083570748>')
        self.prev_button.callback = self.prev_callback
        self.next_button.callback = self.next_callback

        self.add_item(self.prev_button)
        self.add_item(self.next_button)
    
    def reset_embed(self):
        self.embed = discord.Embed(color=0x403c44)
        # embed.add_field(name="Short Input", value=self.children[0].value)
        # embed.add_field(name="Long Input", value=self.children[1].value)
        self.embed.title = f'Slangslation result #{self.i+1}/{self.n}'

        tl = self.translations[self.i]
        self.embed.add_field(name='Target', value=tl['target'], inline=False)
        self.embed.add_field(name='Additional context', value=tl['additional_context'], inline=False)
        self.embed.add_field(name='Slangslation', value=tl['translation'], inline=False)
        self.embed.add_field(name='Explanation', value=tl['explanation'], inline=False)
        self.embed.description = 'hello darkness my old friend'
        self.embed.set_footer(text='Slangslation by Slangslator')
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

