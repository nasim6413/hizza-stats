import os
import discord
from dotenv import load_dotenv
import warnings

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = discord.Bot()  

warnings.filterwarnings(
    "ignore",
    message="Ignoring fixed y limits to fulfill fixed data aspect with adjustable data limits"
)

@bot.event
async def on_ready():
    print('Hizza Stats is running!')

# Load cogs
cogs_list = ['stats', 'balance_history', 'economy', 'next_destiny']

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')
    
bot.run(TOKEN)