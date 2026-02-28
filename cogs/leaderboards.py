import discord
from discord.ext import commands
from services import leaderboards
from utils.enums import STREAK_STATUS
from utils.helpers import fetch_username

class BoardCog(commands.Cog):

    def __init__(self, bot): 
        self.bot = bot
    
    board = discord.SlashCommandGroup("leaderboard", "Check leaderboards.")
        
    @board.command(description='Check streaks leaderboard!')
    async def streaks(self, ctx):
        streaks_board = leaderboards.get_top_streaks()
        
        await ctx.defer()
        
        # Get usernames for ids
        streaks_board['users'] = [await fetch_username(self.bot, user) for user in streaks_board['users']]
        
        # Convert nums to emojis
        streaks_board['claim_status'] = [STREAK_STATUS[i] for i in streaks_board['claim_status']]
        
        output = []
        for i in range(5):
            output.append(
                f"""{i+1}. **{streaks_board['users'][i]}**
                \nDay `{streaks_board['streak_num'][i]}` | Status: {streaks_board['claim_status'][i]}""")
        
        embed = discord.Embed(
            title=f'Streaks Leaderboard',
            description=f'Top 5 users with highest streaks from `{streaks_board['streakers']}` users.'
        )
        
        embed.add_field(
            name='',
            value=(
                "\n".join(output)
            )
        )
        
        await ctx.respond(embed=embed)
    
    @board.command(description='Check who is in danger of losing their streak!')
    async def danger(self, ctx):
        danger_board = leaderboards.get_in_danger()
        
        await ctx.defer()
        # Get usernames for ids
        danger_board['users'] = [await fetch_username(self.bot, user) for user in danger_board['users']]
        
        output = []
        for i in range(len(danger_board)):
            output.append(
                f"""{i+1}. **{danger_board['users'][i]}**
                \nDay `{danger_board['streak_num'][i]}`""")
        
        embed = discord.Embed(
            title=f'Streaks Danger Leaderboard',
            description=f'Users in danger of losing their streaks!'
        )
        
        embed.add_field(
            name='',
            value=(
                "\n".join(output)
            )
        )
        
        
        await ctx.respond(embed=embed)
        
def setup(bot):
    bot.add_cog(BoardCog(bot))