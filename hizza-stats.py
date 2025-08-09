import os
import requests
import discord
from dotenv import load_dotenv
from user_stats import *

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

    embed = discord.Embed(
            title=f'Hizza Stats: {user_name}',
            description='Fun little intro here?',
            color=discord.Colour.blurple()
            )
    
    embed.set_thumbnail(url=avatar_url)
    

    embed.add_field(
        name="HizzaCoin",
        value="* Total claims: ?\n* Biggest claim: ?",
        inline=False
    )
    embed.add_field(
        name="Challenge",
        value="* Total challenges: ?\n* Challenged ? users\n* Challenged by ? users\n* Favourite hand: ?",
        inline=False
    )
    embed.add_field(
        name="Roulette",
        value="* Biggest wager: ?\n* Biggest win: ?\n* Biggest loss: ?",
        inline=False
    )
    await ctx.respond(embed=embed)

### Monthly Hizza report

bot.run(TOKEN)
