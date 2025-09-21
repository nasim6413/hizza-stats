import discord
import datetime
from discord.commands import Option
from discord.ext import commands
from utils.report import HizzaReport
from utils.helpers import fetch_username
from utils.enums import CHALLENGE_HANDS, TIMEFRAMES

class ReportCog(commands.Cog):

    def __init__(self, bot): 
        self.bot = bot
        
    @discord.slash_command(description='Discover Hizza economy activity!')
    async def report(
        self, 
        ctx,  
        timeframe = Option(str, 
                           "Pick a report timeframe", 
                           choices=["lastmonth", "thismonth"],
                           required=False)
    ):
        await ctx.defer()  # prevents interaction timeout
        
        hizza_report = HizzaReport(timeframe)
        
        # Get Hizza account details
        hizza_account = await self.bot.fetch_user(1414255521527238736)
        
        # Fetching Discord names from IDs
        biggest_claimer = await fetch_username(self.bot, hizza_report.coin_results['BiggestClaimer'])
        biggest_coin_giver = await fetch_username(self.bot, hizza_report.coin_results['BiggestCoinGiver'])
        biggest_coin_receiver = await fetch_username(self.bot, hizza_report.coin_results['BiggestCoinReceiver'])
        
        biggest_challenge_winner = await fetch_username(self.bot, hizza_report.challenge_results['BiggestChallengeWinner'])
        biggest_challenge_loser = await fetch_username(self.bot, hizza_report.challenge_results['BiggestChallengeLoser'])

        # Creating embed
        embed = discord.Embed(
                title=f'Hizza {TIMEFRAMES[timeframe]} Stats',
                color=discord.Colour.blurple()
                )
        
        embed.set_thumbnail(url=hizza_account.avatar.url)
        
        embed.add_field(
            name='HizzaCoin',
            value=(
                f"* **{hizza_report.coin_results['TotalClaims']}** total claims by **{len(hizza_report.coin_results['TotalClaimers'])}** users\n"
                f"* **{hizza_report.coin_results['TotalClaimed']}** total coins were claimed\n"
                f"* Biggest claim: **{hizza_report.coin_results['BiggestClaim']}** coins by **{biggest_claimer}**\n"
                f"* There have been **{hizza_report.coin_results['InitialClaims']}** new Hizza fans!\n"
                f"* **{hizza_report.coin_results['TotalCoinGives']}** coins were given amounting to **{hizza_report.coin_results['TotalCoinGiven']}** coins\n"
                f"* Biggest give: **{hizza_report.coin_results['BiggestCoinGive']}** coins from **{biggest_coin_giver}** to **{biggest_coin_receiver}**\n"
            ),
            inline=False
        )

        embed.add_field(
            name='Challenges',
            value=(
                f"* Total challenges: **{hizza_report.challenge_results['TotalChallenges']}**\n"
                f"* Craziest wager: **{biggest_challenge_winner}** won **{hizza_report.challenge_results['BiggestChallengeWin']}** coins from **{biggest_challenge_loser}**\n"
            ),
            inline=False
        )
        
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(ReportCog(bot))