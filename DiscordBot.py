import os
from dotenv import load_dotenv
from discord.ext import commands
import discord
import threading
from utils.query_tool import ask_llm
# from utils.new_tool_class import get_news_info

class Discord_Bot():
    def __init__(self, llm, embed_model, temperature=0.75):
        load_dotenv()
        self.DISCORD_TOKEN = os.getenv('DISCORD_CLIENT_TOKEN')
        
        if not self.DISCORD_TOKEN:
            raise ValueError('DISCORD_CLIENT_TOKEN not found in .env file!')
        
        self.llm = llm
        self.embed_model = embed_model
        self.temperature = temperature

        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix='$', intents=intents)
        self.setup_events()
        self.setup_commands()

    def setup_events(self):
        @self.bot.event
        async def on_ready():
            print(f'{self.bot.user} is online!')

    def setup_commands(self):
        @self.bot.command()
        async def ask(ctx, *, question):
            print(f"Question Received: {question}")
            thinking_msg = await ctx.send("🤔 Let me think about that...")

            response = await ask_llm(question, self.llm, self.temperature)
            print(f"Response:\n {response}")

            await thinking_msg.edit(content=response)
        
        # @self.bot.command()
        # async def news(ctx, *, question):
        #     print(f"Question Received: {question}")
        #     thinking_msg = await ctx.send("🤔 Let me think about that...")
            
        #     response = get_news_info(query=question, llm=self.llm, embed_model=self.embed_model)
        #     print(f"Response:\n {response}")

        #     await thinking_msg.edit(content=response)
        
        @self.bot.command()
        async def h(ctx):
            await ctx.send('Pong!')
    
    def run(self):
        self.bot.run(self.DISCORD_TOKEN)
    
    def start_in_thread(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread