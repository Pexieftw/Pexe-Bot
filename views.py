import discord
import json
from discord.ui import View
from utils import convert

class MovePage(View):
    def __init__(self):
        super().__init__(timeout=20)
        self.commands = json.load(open("Commands.json"))
        self.num = 0

    def _page_embed(self):
        pageTitle = list(self.commands)[self.num]
        embed = discord.Embed(color=0x0080ff, title=pageTitle)
        for key, val in self.commands[pageTitle].items():
            embed.add_field(
                name = key,
                value = val,
                inline = False
            )
        embed.set_footer(text=f"Page {self.num+1} of {len(list(self.commands))}")
        return embed

    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.blurple, custom_id="rewind")
    async def rewind(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.num = 0

        for item in self.children:
            if item.custom_id == "prev":
                item.disabled = True
            if item.custom_id == "next":
                item.disabled = False

        embed = self._page_embed()
        view = self
        await interaction.response.edit_message(embed=embed, view=view)    

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.blurple, custom_id="prev", disabled=True)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.num -= 1
        
        if self.num == 0:
            button.disabled = True
        if self.num != len(list(self.commands))-1:
            for item in self.children:
                if item.custom_id == "next":
                    item.disabled = False

        embed = self._page_embed()
        view = self
        await interaction.response.edit_message(embed=embed, view=view)
        
    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.blurple, custom_id="next")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.num += 1

        if self.num == len(list(self.commands))-1:
            button.disabled = True
        if self.num != 0:
            for item in self.children:
                if item.custom_id == "prev":
                    item.disabled = False

        embed = self._page_embed()
        view = self
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.blurple, custom_id="forward")
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.num = len(list(self.commands))-1

        for item in self.children:
            if item.custom_id == "prev":
                item.disabled = False
            if item.custom_id == "next":
                item.disabled = True

        embed = self._page_embed()
        view = self
        await interaction.response.edit_message(embed=embed, view=view)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(view=self)

'''

    remove the disable completely from this part

'''

class MoveQueue(View):
    def __init__(self, state, is_onepage):
        super().__init__(timeout=20)
        self.state = state
        self.num = 0
        if is_onepage:
            for item in self.children:
                item.disabled = True

    def _queue_embed(self):
        end_page = len(self.state.playlist)//10
        embed = discord.Embed(color=0x0080ff)
        text = ""

        if self.num == end_page:
            for index in range(self.num*10,len(self.state.playlist)):
                text += f"**{index+1}** - `{convert(self.state.playlist[index].duration)}` - {self.state.playlist[index].title}\n"
        else:
            for index in range(self.num*10,self.num*10+10):
                text += f"**{index+1}** - `{convert(self.state.playlist[index].duration)}` - {self.state.playlist[index].title}\n"

        text += "\n**Loop State** = On\n" if self.state.loop else "\n**Loop State** = Off\n"
        embed.add_field(
            name="**Current Queue:**",
            value=text,
            inline=False
        )       
        embed.set_footer(text=f"Page {self.num+1} of {end_page+1}")
        return embed

    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.blurple, custom_id="rewind")
    async def rewind(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.num = 0

        for item in self.children:
            if item.custom_id == "prev":
                item.disabled = True
            if item.custom_id == "next":
                item.disabled = False

        embed = self._queue_embed()
        view = self
        await interaction.response.edit_message(embed=embed, view=view)    

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.blurple, custom_id="prev", disabled=True)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.num -= 1
        
        if self.num == 0:
            button.disabled = True
        if self.num != len(self.state.playlist)//10:
            for item in self.children:
                if item.custom_id == "next":
                    item.disabled = False

        embed = self._queue_embed()
        view = self
        await interaction.response.edit_message(embed=embed, view=view)
        
    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.blurple, custom_id="next")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.num += 1

        if self.num == len(self.state.playlist)//10:
            button.disabled = True
        if self.num != 0:
            for item in self.children:
                if item.custom_id == "prev":
                    item.disabled = False

        embed = self._queue_embed()
        view = self
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.blurple, custom_id="forward")
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.num = len(self.state.playlist)//10

        for item in self.children:
            if item.custom_id == "prev":
                item.disabled = False
            if item.custom_id == "next":
                item.disabled = True

        embed = self._queue_embed()
        view = self
        await interaction.response.edit_message(embed=embed, view=view)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(view=self)
