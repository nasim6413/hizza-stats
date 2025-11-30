# import discord
# from discord.commands import Option
# from discord.ext import commands
# from models.report import HizzaReport
# from utils.helpers import fetch_username
# from utils.enums import CHALLENGE_HANDS, TIMEFRAMES

# class ReportCog(commands.Cog):

#     def __init__(self, bot): 
#         self.bot = bot
        
#     @discord.slash_command(description='Discover Hizza economy activity!')
#     async def report(
#         self, 
#         ctx,  
#         timeframe = Option(str, 
#                            "Pick a report timeframe", 
#                            choices=["alltime", "lastmonth", "thismonth"],
#                            required=False,
#                            default="alltime")
#     ):
#         await ctx.defer()  # prevents interaction timeout
        
#         hizza_report = HizzaReport(timeframe)
#         coin_results = hizza_report.get_coin_results()
#         challenge_results = hizza_report.get_challenge_results()
        
#         # Get Hizza account details
#         hizza_account = await self.bot.fetch_user(1414255521527238736)
        
#         # Fetching Discord names from IDs
#         #TODO: refactor this
#         biggest_claimer = await fetch_username(self.bot, coin_results['BiggestClaimer'])
#         biggest_coin_giver = await fetch_username(self.bot, coin_results['BiggestCoinGiver'])
#         biggest_coin_receiver = await fetch_username(self.bot, coin_results['BiggestCoinReceiver'])
        
#         biggest_challenge_winner = await fetch_username(self.bot, challenge_results['BiggestChallengeWinner'])
#         biggest_challenge_loser = await fetch_username(self.bot, challenge_results['BiggestChallengeLoser'])
#         most_challenge_wins = await fetch_username(self.bot, challenge_results['MostWins'])
#         most_challenge_losses = await fetch_username(self.bot, challenge_results['MostLosses'])

#         # Creating embed
#         embed = discord.Embed(
#                 title=f'Hizza {TIMEFRAMES[timeframe]} Stats',
#                 color=discord.Colour.blurple()
#                 )
        
#         embed.set_thumbnail(url=hizza_account.avatar.url)
        
#         # Coin activity
#         embed.add_field(
#             name='HizzaCoin',
#             value=(
#                 f"* **{coin_results['TotalClaims']}** total claims by **{len(coin_results['TotalClaimers'])}** users\n"
#                 f"* **{coin_results['TotalClaimed']}** total coins were claimed\n"
#                 f"* Biggest claim: **{coin_results['BiggestClaim']}** coins by **{biggest_claimer}**\n"
#                 f"* There have been **{coin_results['InitialClaims']}** new Hizza fans!\n"
#                 f"* **{coin_results['TotalCoinGives']}** coins were given amounting to **{coin_results['TotalCoinGiven']}** coins\n"
#                 f"* Biggest give: **{coin_results['BiggestCoinGive']}** coins from **{biggest_coin_giver}** to **{biggest_coin_receiver}**\n"
#             ),
#             inline=False
#         )

#         # Challenge activity
#         embed.add_field(
#             name='Challenges',
#             value=(
#                 f"* Total challenges: **{challenge_results['TotalChallenges']}**\n"
#                 f"* Craziest wager: **{biggest_challenge_winner}** won **{challenge_results['BiggestChallengeWin']}** coins from **{biggest_challenge_loser}**\n"
#                 f"* Most challenge wins: **{most_challenge_wins}**\n"
#                 f"* Most challenge losses: **{most_challenge_losses}**\n"
#                 f"* Most played hand: **{CHALLENGE_HANDS[challenge_results['MostPlayedHand']]}**\n"
#                 f"* **{CHALLENGE_HANDS[challenge_results['MostWinsHand']]}** won most challenges!\n"
#             ),
#             inline=False
#         )
        
#         embed.set_footer(
#             text='*Roulette stats coming soon!'
#             )
        
#         await ctx.respond(embed=embed)

# def setup(bot):
#     bot.add_cog(ReportCog(bot))