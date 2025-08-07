import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = discord.Bot()

@bot.event
async def on_ready():
    print('Hizza Stats is running!')
    
### Get own statistics
@bot.slash_command(description='Learn more about your Hizza activity!')
async def stats(ctx):
    embed = discord.Embed(
            title="My Amazing Embed",
            description="Embeds are super easy, barely an inconvenience.",
            color=discord.Colour.blurple()
            )

    await ctx.respond("Hello! Here's a cool embed.", embed=embed)

### Monthly Hizza report

bot.run(TOKEN)
