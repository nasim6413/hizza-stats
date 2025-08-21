import discord

async def fetch_username(bot: discord.Bot, user_id):
    if not user_id:
        return "Nobody"
    
    username = await bot.fetch_user(int(user_id))
    if not username:
            return "Nobody"
    else:
            return username.name