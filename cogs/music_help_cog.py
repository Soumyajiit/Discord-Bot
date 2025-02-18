import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot 

        self.help_message = """
```
**General Commands**
[-]help = Displays all Available commands
[-]p <keyword/song name> = Find the song in Youtube and plays it in current voice channel
[-]q = Displays the current music queue
[-]skip = Skips the current song being playes
[-]clear = Stops the ongoing song and clears the queue
[-]pause = Pauses the current song
[-]resumes = Resumes the paused song
[-]leave = Leaves the current voice channel
    
```
"""

        self.text_channel_text = []

    #@commands.Cog.listener()
    #async def on_ready(self):
        #for guild in self.bot.guilds:
            #for channel in guild.text_channels:
                #self.text_channel_text.append(channel)

        #await self.send_to_all(self.help_message)

    async def send_to_all(self, msg):
        for text_channel in self.text_channel_text:
            await text_channel.send(self.help_message) 

    @commands.command(name="help1", aliases=['h'], help="Shows a list of available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)       

async def setup(bot):
    await bot.add_cog(help_cog(bot)) 
