import discord
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import io
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from discord.ext import commands
from models import leaderboard
from utils.helpers import *

class EconomyCog(commands.Cog):

    def __init__(self, bot): 
        self.bot = bot

    @discord.slash_command(description='Hizza economy shares overview.')
    async def economy(
        self, 
        ctx
        ):
        
        await ctx.defer()
    
        economy_shares = leaderboard.get_economy_shares()
        
        # labels and sizes
        labels = list(economy_shares.keys())
        
        avatars = {}
        usernames = []

        for uid in labels:
            if uid == "Others":
                usernames.append(uid)

            else:
                user = await self.bot.fetch_user(int(uid))
                avatar_url = user.display_avatar.url
                
                usernames.append(await fetch_username(self.bot, uid))

                # Fetch profile pictures
                response = requests.get(avatar_url)
                img = Image.open(io.BytesIO(response.content))

                img_resized = img.resize((40, 40), Image.LANCZOS) # Resizing
                avatars[uid] = np.array(img_resized)
    
        sizes = list(economy_shares.values())
        
        fig, ax = plt.subplots(figsize=(8, 8), facecolor="none")
        ax.axis("equal")
        
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,  # remove automatic labels
            autopct="%1.1f%%",
            startangle=140,
            shadow=False,
            textprops={"color": "white", "fontsize": 16},
        )

        for i, autotext in enumerate(autotexts):
            # Get the current position of the % text
            x_pct, y_pct = autotext.get_position()

            # Move username slightly down relative to % text
            y_offset = -0.08
            ax.text(
                x_pct,
                y_pct + y_offset,
                usernames[i],
                ha='center',
                va='center',
                color='white',
                fontsize=12,
                fontweight='bold'
            )

        for i, wedge in enumerate(wedges):
            if usernames[i] == "Others":
                continue

            angle = (wedge.theta2 + wedge.theta1) / 2
            r = 1.15  # outside the pie
            x = r * np.cos(np.deg2rad(angle))
            y = r * np.sin(np.deg2rad(angle))

            uid = labels[i]  # original Discord ID
            imagebox = OffsetImage(avatars[uid], zoom=1.0)
            ab = AnnotationBbox(imagebox, (x, y), frameon=False, box_alignment=(0.5, 0.5))
            ax.add_artist(ab)
        
        # Save to bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        plt.close()
        buf.seek(0)

        # Create discord File
        file = discord.File(buf, filename="economy_plot.png")
        
        # Creating embed
        embed = discord.Embed(
                title=f'Hizza Stats: Economy',
                description=f'Biggest owned shares in the Hizza economy.',
                color=discord.Colour.blurple()
                )
            
        embed.set_image(url="attachment://economy_plot.png")

        await ctx.respond(embed=embed, file=file)

def setup(bot):
    bot.add_cog(EconomyCog(bot))