import os
import discord
from dotenv import load_dotenv
from user_stats import UserStats

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = discord.Bot()

@bot.event
async def on_ready():
    print('Hizza Stats is running!')
    
### Get own statistics
@bot.slash_command(description='Learn more about your Hizza activity!')
async def stats(ctx):

    avatar_url = ctx.user.avatar.url
    user_name = ctx.user.name
    
    user_stats = UserStats(str(ctx.user.id))

    embed = discord.Embed(
            title=f'Hizza Stats: {user_name}',
            description='Discover your Hizza activity!',
            color=discord.Colour.blurple()
            )
    
    embed.set_thumbnail(url=avatar_url)

    embed.add_field(
        name='HizzaCoin',
        value=f'* Total claims: **{user_stats.coin_results['TotalClaims']}** \n* Biggest claim: **{user_stats.coin_results['BiggestClaim']}**',
        inline=False
    )
    embed.add_field(
        name='Challenge',
        value=f'* Total challenges: **{user_stats.challenge_results['TotalChallenges']}**\n* Challenged **{user_stats.challenge_results['TotalChallenger']}** users\n* Challenged by **{user_stats.challenge_results['TotalChallenged']}** users\n* Favourite hand: ?',
        inline=False
    )
    embed.add_field(
        name='Roulette',
        value=f'* **{user_stats.roulette_results['WagerCount']}** wagers\n* Biggest win: **{user_stats.roulette_results['BiggestWin']}**\n* Biggest loss: **{user_stats.roulette_results['BiggestLoss']}**',
        inline=False
    )
    
    
    del user_stats
    await ctx.respond(embed=embed)

### Monthly Hizza report

bot.run(TOKEN)
