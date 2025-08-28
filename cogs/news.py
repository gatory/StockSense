from discord.ext import commands
from utils.news_tool import get_market_news, get_company_news
import asyncio

class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def news(self, ctx):
        try:
            print("News Commands Recieved\n", question)
            response = ask_llm(question, 0.7)
            await ctx.send(response)
            print("Asnwer provided:\n", response)
        except Exception as e:
            await ctx.send(f"Error: {e}")

async def setup(bot):
    await asyncio.gather(
        get_market_news(),
        get_company_news(),
        bot.add_cog(News(bot))
    )