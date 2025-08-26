import discord
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
discord_client_token = os.getenv('DISCORD_CLIENT_TOKEN')

def get_meme():
  response = requests.get('https://meme-api.com/gimme/2')
  data = json.loads(response.text)
  
  return [m["url"] for m in data["memes"]]
  
class MyClient(discord.Client):
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))

  async def on_message(self, message):
    if message.author == self.user:
        return

    if message.content.startswith('$meme'):
        for url in get_meme():
            await message.channel.send(url)

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(discord_client_token) 
