import discord
from discord.ext import commands
from models.next_destiny import next_insane_destiny


class DestinyCog(commands.Cog):

    def __init__(self, bot): 
        self.bot = bot
        
    @discord.slash_command(description='Get the next Insane Destiny date!')
    async def nextdestiny(self, ctx):
        data = next_insane_destiny()
        
        if data['days_left'] == 0:
            embed = discord.Embed(
                title=f"IT'S INSANE DESTINY DAY!!! 🐳",
                description=f"Today is `{data['day']} {data['month']}, {data['year']}`!",
                color=discord.Colour.blurple()
            )
        else:
            embed = discord.Embed(
                title=f"Next INSANE DESTINY 🐳 on:",
                description=f"`{data['day']} {data['month']}, {data['year']}`. That\'s in `{data['days_left']}` days!",
                color=discord.Colour.blurple()
            )
        
        await ctx.respond(embed=embed)
        
def setup(bot):
    bot.add_cog(DestinyCog(bot))