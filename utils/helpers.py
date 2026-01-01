import discord
import requests

async def validate_user(user):
    accounts = requests.get('http://localhost:8080/api/accounts').json()

    account = [acc for acc in accounts if acc['DiscordId'] == str(user.id)]
    if not account:
        return False
    
    return True

async def fetch_username(bot: discord.Bot, user_id):
    if not user_id:
        return "Nobody"
    
    username = await bot.fetch_user(int(user_id))
    if not username:
            return "Nobody"
    else:
            return username.display_name

def whiteify_plot(ax):
    ax.set_facecolor('none')
    for spine in ax.spines.values():
        spine.set_color('white')
    
    ax.tick_params(axis='y', colors='white')
    ax.grid(True, color='gray', alpha=0.3)
    
    return ax