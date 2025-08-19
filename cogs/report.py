import discord
from discord.ext import commands
# from typing import Optional
# from utils.report import

class MyView(discord.ui.View):
    @discord.ui.select( # the decorator that lets you specify the properties of the select menu
        placeholder = "Choose a Flavor!", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="Vanilla",
                description="Pick this if you like vanilla!"
            ),
            discord.SelectOption(
                label="Chocolate",
                description="Pick this if you like chocolate!"
            ),
            discord.SelectOption(
                label="Strawberry",
                description="Pick this if you like strawberry!"
            )
        ]
    )
    
    async def select_callback(self, select, interaction): # the function called when the user is done selecting options
        await interaction.response.send_message(f"Awesome! I like {select.values[0]} too!")

class ReportCog(commands.Cog):

    def __init__(self, bot): 
        self.bot = bot
        
    @discord.slash_command(description='Discover Hizza economy activity!')
    async def report(self, ctx):

        await ctx.respond("Choose a flavour!", view=MyView())
    
def setup(bot):
    bot.add_cog(ReportCog(bot))