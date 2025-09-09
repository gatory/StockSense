import os
from dotenv import load_dotenv
from discord.ext import commands
import discord
import threading
from utils.query_tool import ask_llm
from utils.news_tool import get_news_info
from utils.yt_tool import YoutubeTool

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
        self.youtube = YoutubeTool()

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
        
        @self.bot.command()
        async def news(ctx, symbol=None, *, question):
            print(f"Question Received: {question} about {symbol}")
            thinking_msg = await ctx.send("🤔 Let me think about that...")
            
            response = get_news_info(query=question, llm=self.llm, embed_model=self.embed_model, symbol=symbol)
            print(f"Response:\n {response}")

            await thinking_msg.edit(content=response)

        @self.bot.command()
        async def news(ctx, yt_link, *, question):
            print(f"Question Received: {question} about {yt_link}")
            thinking_msg = await ctx.send("🤔 Let me think about that...")
            
            response = self.youtube.summarize_youtube(llm=self.llm, embed_model=self.embed_model, query=question)
            print(f"Response:\n {response}")

            await thinking_msg.edit(content=response)
        
        @self.bot.command()
        async def h(ctx):
            await ctx.send('Pong!')
    
    def run(self):
        self.bot.run(self.DISCORD_TOKEN)
    
    def start_in_thread(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread