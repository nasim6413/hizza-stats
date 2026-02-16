import discord
from discord.ext import commands
from services.destiny import next_insane_destiny, tomorrow_destiny
from utils.enums import DESTINY

class DestinyCog(commands.Cog):

    def __init__(self, bot): 
        self.bot = bot
        
    @discord.slash_command(description='Get the next Insane Destiny date!')
    async def insanedestiny(self, ctx):
        data = next_insane_destiny()
        
        if data['days_left'] == 0:
            embed = discord.Embed(
                title=f"IT'S INSANE DESTINY DAY!!! 🐳",
                description=f"Today is `{data['day']} {data['month']}, {data['year']}`!",
                color=discord.Colour.blurple()
            )
        else:
            if data['days_left'] == 1:
                days_string = f"TOMORROW!"
            else:
                days_string = f"in `{data['days_left']}` days!"
            
            embed = discord.Embed(
                title=f"Next INSANE DESTINY 🐳 on:",
                description=f"`{data['day']} {data['month']}, {data['year']}`. That\'s {days_string} ",
                color=discord.Colour.blurple()
            )
        
        await ctx.respond(embed=embed)
        
    @discord.slash_command(description='Get tomorrow\'s Destiny forecast!')
    async def tomorrow(self, ctx):
        destiny_num = tomorrow_destiny()
        
        embed = discord.Embed(
            title=f"Tomorrow will be `{DESTINY[destiny_num]}` DESTINY 🐳!",
            color=discord.Colour.blurple()
        )
        
        await ctx.respond(embed=embed)
        
def setup(bot):
    bot.add_cog(DestinyCog(bot))