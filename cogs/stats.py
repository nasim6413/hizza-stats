import discord
from discord.ext import commands
from typing import Optional
from utils.stats import UserStats
from utils.helpers import fetch_username

class UserCog(commands.Cog):

    def __init__(self, bot): 
        self.bot = bot
        
    @discord.slash_command(description='Learn more about your Hizza activity!')
    async def stats(self, ctx, user: Optional[discord.Member]):
        
        if not user:
            user = ctx.user
            
        avatar_url = user.avatar.url
        user_name = user.name
        
        user_stats = UserStats(str(user.id))
        
        # Fetching usernames from user_id
        biggest_give_to = await fetch_username(self.bot, user_stats.coin_results['BiggestGiveTo'])
        biggest_given_from = await fetch_username(self.bot, user_stats.coin_results['BiggestGivenFrom'])
        
        # Creating embed
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
                f"* Biggest claim: **{user_stats.coin_results['BiggestClaim']}** coins\n"
                f"* Total given: **{user_stats.coin_results['TotalGiveAmount']}** coins\n"
                f"* Biggest give: **{user_stats.coin_results['BiggestGive']}** coins to **{biggest_give_to}**\n"
                f"* Total received: **{user_stats.coin_results['TotalGivenAmount']}** coins\n"
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
                f"* Total won: **{user_stats.roulette_results['TotalWon']}** coins\n"
                f"* Biggest win: **{user_stats.roulette_results['BiggestWin']}** coins\n"
                f"* Total lost: **{user_stats.roulette_results['TotalLost']}** coins\n"
                f"* Biggest loss: **{user_stats.roulette_results['BiggestLoss']}** coins"
            ),
            inline=False
        )

        await ctx.respond(embed=embed)
    
def setup(bot):
    bot.add_cog(UserCog(bot))