import os
import discord
from dotenv import load_dotenv
from typing import Optional
from user_stats import UserStats

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = discord.Bot()  

@bot.event
async def on_ready():
    print('Hizza Stats is running!')
    
### Get own statistics
@bot.slash_command(description='Learn more about your Hizza activity!')
async def stats(ctx, user: Optional[discord.Member]):
    
    if not user:
        user = ctx.user
        
    avatar_url = user.avatar.url
    user_name = user.name
    
    user_stats = UserStats(str(user.id))
    
    # Fetching usernames from user_id
    biggest_give_to = user_stats.coin_results['BiggestGiveTo']
    biggest_given_from = user_stats.coin_results['BiggestGivenFrom']
    
    
    biggest_give_to = await bot.fetch_user(int(biggest_give_to)) if biggest_give_to else None
    biggest_give_to = biggest_give_to.name if biggest_give_to else 'Nobody'
    biggest_given_from = await bot.fetch_user(int(biggest_given_from)) if biggest_given_from else None
    biggest_given_from = biggest_given_from.name if biggest_given_from else 'Nobody'

    embed = discord.Embed(
            title=f'Hizza Stats: {user_name}',
            description='Discover your Hizza activity!',
            color=discord.Colour.blurple()
            )
    
    embed.set_thumbnail(url=avatar_url)

    embed.add_field(
        name='HizzaCoin',
        value=(
            f"* Total claims: **{user_stats.coin_results['TotalClaims']}**\n"
            f"* Biggest claim: **{user_stats.coin_results['BiggestClaim']}**\n"
            f"* Coin given: **{user_stats.coin_results['TotalGiveAmount']}** coins\n"
            f"* Biggest give: **{user_stats.coin_results['BiggestGive']}** coins to **{biggest_give_to}**\n"
            f"* Coin received: **{user_stats.coin_results['TotalGivenAmount']}** coins\n"
            f"* Biggest received: **{user_stats.coin_results['BiggestGiven']}** coins from **{biggest_given_from}**"

        ),
        inline=False
    )
    
    embed.add_field(
        name='Challenge',
        value=(
            f"* Total challenges: **{user_stats.challenge_results['TotalChallenges']}**\n"
            f"* Challenged **{user_stats.challenge_results['TotalChallenger']}** users\n"
            f"* Challenged by **{user_stats.challenge_results['TotalChallenged']}** users\n"
            f"* Favourite hand: **{user_stats.challenge_results['FavouriteHand']}**"
        ),
        inline=False
    )

    embed.add_field(
        name='Roulette',
        value=(
            f"* **{user_stats.roulette_results['WagerCount']}** wagers\n"
            f"* Biggest win: **{user_stats.roulette_results['BiggestWin']}**\n"
            f"* Biggest loss: **{user_stats.roulette_results['BiggestLoss']}**"
        ),
        inline=False
    )

    del user_stats
    await ctx.respond(embed=embed)

### Monthly Hizza report

bot.run(TOKEN)
