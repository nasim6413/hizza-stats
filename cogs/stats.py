import discord
from discord.ext import commands
from typing import Optional
from models.stats import UserStats
from utils.helpers import fetch_username

class UserCog(commands.Cog):

    def __init__(self, bot): 
        self.bot = bot
        
    @discord.slash_command(description='Learn more about your Hizza activity!')
    async def stats(self, ctx, user: Optional[discord.Member]):
        await ctx.defer()
        
        if not user:
            user = ctx.user
            
        avatar_url = user.avatar.url
        user_name = user.name
        
        user_stats = UserStats(str(user.id))
        coin_results = user_stats.get_coin_results()
        challenge_results = user_stats.get_challenge_results()
        roulette_results = user_stats.get_roulette_results()
        
        # Fetching usernames from user_id
        biggest_give_to = await fetch_username(self.bot, coin_results['BiggestGiveTo'])
        biggest_given_from = await fetch_username(self.bot, coin_results['BiggestGivenFrom'])
        
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
                f"* Total claims: **{coin_results['TotalClaims']}**\n"
                f"* Biggest claim: **{coin_results['BiggestClaim']}** coins\n"
                f"* Total given: **{coin_results['TotalGiveAmount']}** coins\n"
                f"* Biggest give: **{coin_results['BiggestGive']}** coins to **{biggest_give_to}**\n"
                f"* Total received: **{coin_results['TotalGivenAmount']}** coins\n"
                f"* Biggest received: **{coin_results['BiggestGiven']}** coins from **{biggest_given_from}**"

            ),
            inline=False
        )
        
        embed.add_field(
            name='Challenge',
            value=(
                f"* Total challenges: **{challenge_results['TotalChallenges']}**\n"
                f"* Challenged **{challenge_results['TotalChallenger']}** users\n"
                f"* Challenged by **{challenge_results['TotalChallenged']}** users\n"
                f"* Favourite hand: **{challenge_results['FavouriteHand']}**"
            ),
            inline=False
        )

        embed.add_field(
            name='Roulette',
            value=(
                f"* **{roulette_results['WagerCount']}** wagers\n"
                f"* Total won: **{roulette_results['TotalWon']}** coins\n"
                f"* Biggest win: **{roulette_results['BiggestWin']}** coins\n"
                f"* Total lost: **{roulette_results['TotalLost']}** coins\n"
                f"* Biggest loss: **{roulette_results['BiggestLoss']}** coins"
            ),
            inline=False
        )

        await ctx.respond(embed=embed)
    
def setup(bot):
    bot.add_cog(UserCog(bot))