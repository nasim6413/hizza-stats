import discord
from datetime import datetime

async def fetch_username(bot: discord.Bot, user_id):
    if not user_id:
        return "Nobody"
    
    username = await bot.fetch_user(int(user_id))
    if not username:
            return "Nobody"
    else:
            return username.name
        
def fetch_months(timeframe):
    today = datetime.now()
    
    if timeframe == 'thismonth':
        month = today.month
        year = today.year

    elif timeframe == 'lastmonth':
        if today.month == 1:  # January → go to previous December
            month = 12
            year = today.year - 1
        else:
            month = today.month - 1
            year = today.year
            
    else:
        month = None
        year = None
        
    return month, year