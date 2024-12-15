import discord
from copy import deepcopy
from aiTest import generate_explanation

class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(
            label="Source (SLANG)",
            placeholder='Enter source slang',
            max_length=50,
        ))
        self.add_item(discord.ui.InputText(
            label="Source language",
            placeholder='Enter source language',
            max_length=20,
        ))
        self.add_item(discord.ui.InputText(
            label="Target language",
            placeholder='Enter destination language',
            max_length=20,
        ))
        self.add_item(discord.ui.InputText(
            label="Additional context",
            placeholder="Enter surrounding text as context for higher translation accuracy",
            style=discord.InputTextStyle.long,
            max_length=250,
            required=False
        ))

    async def callback(self, interaction: discord.Interaction):
        # embed = discord.Embed(title="Modal Results")
        # embed.add_field(name="Short Input", value=self.children[0].value)
        # embed.add_field(name="Long Input", value=self.children[1].value)
        source = self.children[0].value
        source_language = self.children[1].value
        target_language = self.children[2].value
        additional_context = self.children[3].value

        # translations = [
        #     {
        #         'source': source,
        #         'target_language': target_language,
        #         'additional_context': additional_context,
        #         'translation': 'ni hao ma',
        #         'explanation': 'Yada yada explanation exoplanation',
        #         'use_cases': 'bob ross',
        #     },
        #     {
        #         'source': source,
        #         'target_language': target_language,
        #         'additional_context': additional_context,
        #         'translation': 'pien',
        #         'explanation': 'a wejo iasjdfl kasdjflk j',
        #         'use_cases': 'ur mom',
        #     },
        # ]
        view = MyView(None)
        view.message = await interaction.response.send_message(embed=view.embed, view=view)
        view.translations = await generate_explanation(
            source=source,
            source_language=source_language,
            target_language=target_language,
            additional_context=additional_context,
            response_amount=2,
            max_tokens=800,
        )
        view.n = len(view.translations)
        view.reset_embed()
        await view.message.edit(embed=view.embed, view=view)


class MyView(discord.ui.View):
    def __init__(self, translations: dict[dict] | None):
        super().__init__()

        self.translations = deepcopy(translations) if translations is not None else None

        self.i = 0
        self.n = len(self.translations) if translations is not None else 1

        self.reset_embed()
        
        self.prev_button = discord.ui.Button(emoji='<:left:940157746723061810>')
        self.next_button = discord.ui.Button(emoji='<:right:940157728083570748>')
        self.prev_button.callback = self.prev_callback
        self.next_button.callback = self.next_callback

        self.add_item(self.prev_button)
        self.add_item(self.next_button)
    
    def reset_embed(self):
        self.embed = discord.Embed(color=0x403c44)
        if self.translations is None:
            self.embed.description = 'Loading...'
            return
        # embed.add_field(name="Short Input", value=self.children[0].value)
        # embed.add_field(name="Long Input", value=self.children[1].value)

        self.embed.title = f'Slangslation result #{self.i+1}/{self.n}'

        tl = self.translations[self.i]

        print(tl)
        if 'error' in tl:
            self.embed.add_field(name='Error', value=tl['error'], inline=False)
        else:
            self.embed.add_field(name='Source (slang)', value=tl['source'], inline=True)
            self.embed.add_field(name='Source language', value=tl['source_language'], inline=True)
            self.embed.add_field(name='Target language', value=tl['target_language'], inline=True)
            self.embed.add_field(name='Additional context', value=tl['additional_context'], inline=False)
            self.embed.add_field(name='Slangslation', value=tl['translation'], inline=True)
            self.embed.add_field(name='Explanation', value=tl['explanation'], inline=True)
            self.embed.add_field(name='Use cases', value='\n'.join('- '+case for case in tl['use_cases']), inline=True)
            self.embed.description = 'Slangslation successful!'
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

