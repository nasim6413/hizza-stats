import discord
import matplotlib.pyplot as plt
import io
from discord.ext import commands
from discord.commands import Option
from datetime import timedelta
from models import balance_history
from utils.helpers import fetch_username

class BalanceCog(commands.Cog):

    def __init__(self, bot): 
        self.bot = bot
        
    balance = discord.SlashCommandGroup("balancehistory", "Check balance histories.")

    @balance.command(description='Check a user\'s balance history.')
    async def user(
        self, 
        ctx, 
        mode = Option(str,
                      "Pick balance history mode",
                      choices=["l30days", "l100transactions"],
                      required=False,
                      default="l30days"),
        user = Option(discord.Member, 
                    "Pick a user", 
                    required=False,
                    default=False)
        ):
        await ctx.defer()
        
        if not user:
            user = ctx.user
            
        #TODO: error handling            
        avatar_url = user.avatar.url
        user_name = user.name
        
        if mode == "l30days":
            # Plot historical balance l30d
            l30d_balances = balance_history.get_historical_balance(str(user.id))   
            
            dates = sorted(l30d_balances.keys()) # Sorts dates
            end_vals = [int(l30d_balances[d]["end_balance"]) for d in dates]

            plt.figure(figsize=(10, 6), facecolor='none')
            
            ax = plt.gca()
            ax.set_facecolor('none')  # transparent axes background
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white') 
            ax.spines['left'].set_color('white') 
            ax.spines['right'].set_color('white')

            # Plot line with a bright color
            hex_colour = f"#{user.color.value:06x}"
            plt.plot(dates, end_vals, color=hex_colour, linewidth=2)

            # Starts and ends x axis at correct dates
            pad = timedelta(days=1)
            ax.set_xlim(dates[0] - pad, dates[-1] + pad)
            
            # Set x ticks as dates
            ax.set_xticks(dates)  # only real dates get labels
            ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in dates], rotation=45, ha='right', color='white')
            plt.xticks(rotation=45, ha='right', color='white')

            # Labels
            ax.set_xlabel("Date", color='white')
            ax.set_ylabel("Balance by End of Day", color='white')
            ax.set_title("Hizza Balance Last 30 Days", color='white')
            ax.tick_params(axis='y', colors='white')
            ax.grid(True, color='gray', alpha=0.3)

            plt.tight_layout()
                    
            # Save to bytes buffer instead of file
            buf = io.BytesIO()
            plt.savefig(buf, format="png", transparent=True)
            plt.close()
            buf.seek(0)

            # Create discord File
            file = discord.File(buf, filename="end_balance.png")
            
            # Creating embed
            embed = discord.Embed(
                    title=f'Hizza Stats: {user_name}',
                    description=f'User balance history for the past 30 days.',
                    color=discord.Colour.blurple()
                    )

            embed.set_thumbnail(url=avatar_url)
                
            embed.set_image(url="attachment://end_balance.png")
        
        if mode == "l100transactions":
            l100transactions = balance_history.get_transaction_history(str(user.id))

            x = range(len(l100transactions))
            balances = [int(l100transactions[i]) for i in x]

            plt.figure(figsize=(10, 6), facecolor='none')
            
            ax = plt.gca()
            ax.set_facecolor('none')  # transparent axes background
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white') 
            ax.spines['left'].set_color('white') 
            ax.spines['right'].set_color('white')

            # Plot line with a bright color
            hex_colour = f"#{user.color.value:06x}"
            
            plt.plot(
                x,
                balances,
                color=hex_colour,
                linewidth=2
            )

            plt.xticks(ha='right', color='white')
            
            # Labels
            ax.set_xlabel("Transactions", color='white')
            ax.set_ylabel("Balance by Last 100 Transactions", color='white')
            ax.invert_xaxis()
            ax.set_title("Hizza Balance Last 100 Transactions", color='white')
            ax.tick_params(axis='y', colors='white')
            ax.grid(True, color='gray', alpha=0.3)

            plt.tight_layout()
                    
            # Save to bytes buffer instead of file
            buf = io.BytesIO()
            plt.savefig(buf, format="png", transparent=True)
            plt.close()
            buf.seek(0)

            # Create discord File
            file = discord.File(buf, filename="end_balance.png")
            
            # Creating embed
            embed = discord.Embed(
                    title=f'Hizza Stats: {user_name}',
                    description=f'User balance history for the past 100 transactions.',
                    color=discord.Colour.blurple()
                    )

            embed.set_thumbnail(url=avatar_url)
                
            embed.set_image(url="attachment://end_balance.png")
            
        await ctx.respond(embed=embed, file=file)

    @balance.command(description='Check current leaderboard top 5 user balances for the past 30 days.')
    async def top5(
        self, 
        ctx
        ):
        await ctx.defer()
        
        # Plot historical balance l30d for top 5 users
        top5_balances = balance_history.get_top5_historical_balance()

        plt.figure(figsize=(10, 6), facecolor='none')
        ax = plt.gca()
        ax.set_facecolor('none')

        # Spine colors
        for spine in ax.spines.values():
            spine.set_color('white')

        for user_id, l30d_balances in top5_balances.items():
            if not l30d_balances:
                continue

            dates = sorted(l30d_balances.keys())
            end_vals = [
                int(l30d_balances[d]["end_balance"])
                for d in dates
            ]

            username = await fetch_username(self.bot, user_id)
            plt.plot(dates, end_vals, linewidth=2, label=username)

        # Starts and ends x axis at correct dates
        pad = timedelta(days=1)
        ax.set_xlim(dates[0] - pad, dates[-1] + pad)
        
        # Set x ticks as dates
        ax.set_xticks(dates)  # only real dates get labels
        ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in dates], rotation=45, ha='right', color='white')
        plt.xticks(rotation=45, ha='right', color='white')

        # Labels & title
        ax.set_xlabel("Date", color='white')
        ax.set_ylabel("Balance by End of Day", color='white')
        ax.set_title("Top 5 Users – Balance Last 30 Days", color='white')

        ax.tick_params(axis='y', colors='white')
        ax.grid(True, color='gray', alpha=0.3)

        # Legend
        legend = ax.legend(
            title="User",
            facecolor='none',
            edgecolor='white'
        )
        plt.setp(legend.get_texts(), color='white')
        plt.setp(legend.get_title(), color='white')

        plt.tight_layout()

        # Save to bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png", transparent=True)
        plt.close()
        buf.seek(0)

        # Create discord File
        file = discord.File(buf, filename="end_balance.png")
        
        # Creating embed
        embed = discord.Embed(
                title=f'Hizza Stats: Leaderboard',
                description=f'Current top 5 balance history for the past 30 days.',
                color=discord.Colour.blurple()
                )
            
        embed.set_image(url="attachment://end_balance.png")

        await ctx.respond(embed=embed, file=file)

def setup(bot):
    bot.add_cog(BalanceCog(bot))