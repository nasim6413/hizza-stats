import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = discord.Bot()  

@bot.event
async def on_ready():
    print('Hizza Stats is running!')

# Load cogs
cogs_list = ['stats', 'report']

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')
    
bot.run(TOKEN)
