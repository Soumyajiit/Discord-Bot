from ast import alias
from importlib.resources import contents
import typing
import discord
from discord.ext import commands
import random
from discord import app_commands
from token_1 import DISCORD_TOKEN
import os


token = DISCORD_TOKEN

MY_GUILD = discord.Object(id=0)

    

description = '''First bot'''
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='-', description=description, intents=intents)


initial_extensions = []




@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
   
@bot.event
async def setup_hook():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            initial_extensions.append("cogs." + filename[:-3])
    print("Bot is starting")
    await bot.load_extension("cogs.slash")
    await bot.load_extension("cogs.music_cog")
    await bot.load_extension("cogs.music_help_cog")
    


@bot.command(name='say')
async def audit(ctx, *, text):
    """Says the given Message"""
    message = ctx.message
    await message.delete()

    await ctx.send(f"{text}")

@bot.command()
async def ping(ctx):
    """Shows latency of bot"""
    await ctx.send(f"{(round(bot.latency*1000))} ms")


@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


@bot.command()
async def dm(ctx, user: discord.User = None, *args):
    """Lets user anonymously DM another user"""
    content = ' '.join(args)
    if user == ctx.message.author:
        await ctx.send("You can't DM yourself, goofy!")
        return
    
    # Check if a user and message were provided
    if user is None:
        await ctx.send(f'**{ctx.message.author},** Please mention someone to DM.')
        return
    if not content:
        await ctx.send(f'**{ctx.message.author},** Please provide a message to send.')
        return
    
    # Try to send the DM and handle any exceptions
    try:
        await ctx.message.delete()  # Delete the original message for anonymity
        await user.send(f'{content}')
        await ctx.send(f"Message sent to {user.name} successfully.")
    except discord.Forbidden:
        await ctx.send(f"Sorry, {ctx.message.author}, I can't send a DM to {user.name}. They may have DMs disabled.")
    except discord.HTTPException:
        await ctx.send(f"Failed to send the message to {user.name} due to a network error.")


@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))


@bot.command()
@commands.has_role('Kazu')
async def dmspam(ctx, times: int, user: discord.User = None, *args):
    """Repeats a dm multiple times."""
    content = ' '.join(args)
    if user == ctx.message.author:
        await ctx.send("You can't DM yourself goofy")
        return
    else:
        await ctx.message.delete()
    if user == None:
      await ctx.send(f'**{ctx.message.author},** Please mention somebody to DM.')
    else:
      if content == None:
        await ctx.send(f'**{ctx.message.author},** Please send a message to DM.')
      else:
        for i in range(times):
            await user.send(f'{content}')

@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)


@bot.command()
async def jointime(ctx, member: discord.Member = None):
    """Says when a member joined."""
    # If no member is provided, default to the command invoker
    if member is None:
        member = ctx.author
    
    # Check if the bot can access the join date
    if member.joined_at is None:
        await ctx.send("Unable to retrieve the join date for this member.")
        return
    
    # Format and send the join date
    join_date = discord.utils.format_dt(member.joined_at, style="F")  # Style "F" provides a full timestamp
    await ctx.send(f'{member.name} joined on {join_date}')



@bot.group()
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send(f'No, {ctx.subcommand_passed} is not cool')


@cool.command(alias='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')

@bot.command()
async def avatar(ctx, user: discord.User = None):
    """shows the avatar of user"""
    if user == None:
        user = ctx.author
    useravatar = user.avatar.url

    userembed = discord.Embed(title=f"{user.name}'s Avatar", colour=user.colour,timestamp=ctx.message.created_at)
    userembed.set_image(url = useravatar)

    await ctx.send(embed = userembed) 

@bot.command()
async def userinfo(ctx, *, user: discord.Member = None): # b'\xfc'
    """Shows basic Userinfo"""
    if user is None:
        user = ctx.author      
    date_format = "%a, %d %b %Y %I:%M %p"
    embed = discord.Embed(color=user.colour, description=user.mention)
    embed.set_author(name=str(user), icon_url=user.avatar.url)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="Joined", value=user.joined_at.strftime(date_format))
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    embed.add_field(name="Join position", value=str(members.index(user)+1))
    embed.add_field(name="Registered", value=user.created_at.strftime(date_format))
    if len(user.roles) > 1:
        role_string = ' '.join([r.mention for r in user.roles][1:])
        embed.add_field(name="Roles [{}]".format(len(user.roles)-1), value=role_string, inline=False)
    perm_string = ', '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
    embed.add_field(name="Guild permissions", value=perm_string, inline=False)
    embed.set_footer(text='ID: ' + str(user.id))
    return await ctx.send(embed=embed)


@bot.command()
async def waifu(ctx, *, user: discord.Member = None):
    """sends a cute Waifu picture"""
    if user is None:
        user = ctx.author 
    responses = ["https://cdn.discordapp.com/attachments/908398857501683742/979610676802781194/illust_91951205_20220527_090956.jpg", "https://cdn.discordapp.com/attachments/908398857501683742/979610823255277568/illust_92818201_20220527_090135.jpg", "https://cdn.discordapp.com/attachments/908398857501683742/979610823255277568/illust_92818201_20220527_090135.jpg", "https://media.discordapp.net/attachments/966650671321473024/1033757301087162428/image.jpg?width=291&height=467", "https://cdn.discordapp.com/attachments/908398857501683742/955404406206136330/94038993_p0_master1200.jpg", "https://cdn.discordapp.com/attachments/908398857501683742/979610677385777173/illust_97765275_20220527_090043.jpg", "https://cdn.discordapp.com/attachments/908398857501683742/979610677113151498/illust_97468383_20220527_090128.jpg"]
    response = random.choice(responses)
    embed = discord.Embed(color=ctx.author.colour, description=user.mention)
    embed.set_image(url=f'{response}')
    await ctx.send(embed=embed)



@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: typing.Optional[typing.Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return
    
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please provide all required arguments.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("This command does not exist.")
        elif isinstance(error, commands.MissingRole):
            await ctx.send("You don't have the required role to run this command.")
    # Handle other error types as needed


    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

bot.run(token)