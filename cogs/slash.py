from ast import alias
import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyCxM9G2fQ_3X7H78yYZz4yACfl3EaarYew"

genai.configure(api_key=GEMINI_API_KEY)


class slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        
    @app_commands.command(name="hello")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hey {interaction.user.mention}! How is your day going?", ephemeral=True)


    @app_commands.command(name="say")
    @app_commands.describe(arg="what should I say?")
    async def say(self, interaction: discord.Interaction, arg: str):
        await interaction.response.send_message(f"{interaction.user.name} said: '{arg}'  ")


    @app_commands.command(name="mention")
    @app_commands.describe(mention="mention someone", text="what should I say?")
    async def mention(self, interaction: discord.Interaction, text: str, mention: discord.Member):
        member = mention or interaction.user
        await interaction.response.send_message(f"{mention.mention} {text} ")


    @app_commands.command(name="gpt", description="Get a response from OpenAI's GPT model")
    @app_commands.describe(prompt="What should I say?")
    async def gpt(self, interaction: discord.Interaction, prompt: str):
        try:
            response = genai.generate(prompt=prompt)
            text_response = response.text
            await interaction.response.send_message(text_response)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(slash(bot))
    