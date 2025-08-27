import os
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_CLIENT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

async def load_extensions():
    try:
        await bot.load_extension("cogs.inform")
        print("Successfully loaded cogs.inform")
    except Exception as e:
        print(f"[ERROR] Failed to load cog 'cogs.inform': {e}")

async def main():
    await load_extensions()
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())