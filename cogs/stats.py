import discord
from discord.ext import commands
from discord.commands import Option
from models.stats import UserStats
from utils.helpers import fetch_username
from utils.enums import TIMEFRAMES, CHALLENGE_HANDS

class UserCog(commands.Cog):

    def __init__(self, bot): 
        self.bot = bot
        
    @discord.slash_command(description='Learn more about your Hizza activity!')
    async def stats(
        self, 
        ctx, 
        user = Option(discord.Member, 
                     "Pick a user", 
                     required=False,
                     default=None)
        ):
        await ctx.defer()
        
        if not user:
            user = ctx.user
            
        avatar_url = user.avatar.url
        user_name = user.name
        
        user_stats = UserStats(str(user.id))
        coin_results = user_stats.get_coin_results()
        challenge_results = user_stats.get_challenge_results()
        roulette_results = user_stats.get_roulette_results()
        
        # # Fetching usernames from user_id
        # biggest_give_to = await fetch_username(self.bot, coin_results['BiggestGiveTo'])
        # biggest_given_from = await fetch_username(self.bot, coin_results['BiggestGivenFrom'])
        
        # Creating embed
        embed = discord.Embed(
                title=f'Hizza Stats: {user_name}',
                description=f'Discover your Hizza activity!',
                color=discord.Colour.blurple()
                )
        
        embed.set_thumbnail(url=avatar_url)

        if coin_results:
            embed.add_field(
                name='HizzaCoin',
                value=(
                    f"* Claimed **{coin_results['TotalClaims']}** times\n"
                    f"* Claimed **{coin_results['TotalClaimed']}** coins in total\n"
                    f"* Best claim: **{coin_results['BestClaim']}** coins\n"
                    f"* Total coins given: **{coin_results['TotalGiveAmount']}** coins\n"
                    f"* Total coins received: **{coin_results['TotalGivenAmount']}** coins\n"
                ),
                inline=False
            )
        
        if challenge_results:
            embed.add_field(
                name='Challenge',
                value=(
                    f"* Participated in **{challenge_results['TotalChallenges']}** challenges\n"
                    f"* Challenged **{challenge_results['TotalChallenger']}** users\n"
                    f"* Has been challenged by **{challenge_results['TotalChallenged']}** users\n"
                    f"* Favourite hand: **{challenge_results['FavouriteHand'] if not None else 'Unpredictable...'}**"
                ),
                inline=False
            )

        if roulette_results:
            embed.add_field(
                name='Roulette',
                value=(
                    f"* **Placed {roulette_results['WagerCount']}** wagers\n"
                    f"* Total won: **{roulette_results['TotalWon']}** coins\n"
                    f"* Biggest win: **{roulette_results['BiggestWin']}** coins\n"
                    f"* Total lost: **{roulette_results['TotalLost']}** coins\n"
                    f"* Biggest loss: **{roulette_results['BiggestLoss']}** coins\n"
                    f"* Favourite game: **{roulette_results['FavouriteGame'] if not None else 'What a gambler...'}** coins"
                ),
                inline=False
            )
        
        embed.set_footer(
            text='*More stats coming soon!'
            )

        await ctx.respond(embed=embed)
    
def setup(bot):
    bot.add_cog(UserCog(bot))