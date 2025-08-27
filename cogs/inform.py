from discord.ext import commands
from utils.query_tool import ask_llm

class Inform(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def ask(self, ctx, *, question = None):
        if not question:
            await ctx.send("Please provide a question: '$ask your question here'")
            return
        try:
            print("Question Recieved:\n", question)
            response = ask_llm(question, 0.7)
            await ctx.send(response)
            print("Asnwer provided:\n", response)
        except Exception as e:
            await ctx.send(f"Error: {e}")

async def setup(bot):
    await bot.add_cog(Inform(bot))