import os
import aiohttp
import math
import openai
import requests
import tiktoken
import discord
from discord import app_commands
from termcolor import colored
from io import BytesIO

def num_tokens_from_string(string: str, encoding_name: str) -> int:
  encoding = tiktoken.get_encoding(encoding_name)
  num_tokens = len(encoding.encode(string))
  return num_tokens

messages = [
  {"role": "system", "content": """You are a festive AI discord bot that ONLY answers questions about winter holidays and festivities, as well as generate songs. Otherwise, you will politely guide the conversation back to winter festivities.
  Your discord invite link: https://discord.com/oauth2/authorize?client_id=1313504973450907700
  Avoid improper indentation and spelling, and remember to put spaces between words and after punctuation.
  You can generate at most 2000 characters
  """},
]

tokensUsed = 0
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="The winter is the best!"))
  await tree.sync()
  print(f'We have logged in as {client.user}')

import tempfile

def chat(prompt):
    global messages, tokensUsed
    openai.api_key = os.environ["AI"]
    message = prompt
    messages.append(
        {"role": "user", "content": message},
    )
    chat = openai.ChatCompletion.create(
        model = "ftjob-d30wKS01Q6zG1pXVDq5JQpJl", messages = messages, temperature = 0.5, max_completion_tokens = 500
    )
    reply = chat.choices[0].message.content
    if len(reply) > 2000:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(reply.encode())
            temp_file_path = temp_file.name
        return discord.File(temp_file_path)
    messages.append({"role": "assistant", "content": reply})
    return reply

@tree.command(name="image", description="Use FestiveBot's AI to generate images! It will generate a festive version what you want!")
async def image_command(interaction: discord.Interaction, object: str):
    try:
        await interaction.response.defer()
        openai.api_key = os.environ["AI"]
        response = openai.Image.create(
            model="dall-e-3",
            prompt="Make a festive version of: " + object,
            n=1,
            size="1024x1024",
        )
        url = response["data"][0]["url"]
        image_data = requests.get(url).content
        image_file = discord.File(BytesIO(image_data), filename="image.png")
        await interaction.followup.send("Your image:", file=image_file)
    except Exception as e:
        await interaction.followup.send("There was an error generating the image.")

@tree.command(name="song", description="Write a random festive song!")
async def song_command(interaction):
  global tokens
  print("Recieved interaction \"/song\"")
  await interaction.response.defer()
  gpt = chat("Write a festive holiday song about winter joy.")
  if isinstance(gpt, discord.File):
    await interaction.followup.send(gpt)
  await interaction.followup.send(gpt)

@client.event
async def on_message(message):
    print(f"Received normal interaction: {message}")
    if message.author == client.user:
        return
    elif isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            gpt = chat(message.content)
        print(f"Generated response for normal interaction with interaction {message.content}: {gpt}")
        if isinstance(gpt, discord.File):
            await message.channel.send("The response was too long, here is a text file with the details:", file=gpt)
        else:
            await message.channel.send(gpt)
    elif isinstance(message.channel, discord.TextChannel) and client.user in message.mentions:
        async with message.channel.typing():
            gpt = chat(message.content)
        print(f"Generated response for normal interaction with interaction {message.content}: {gpt}")
        if isinstance(gpt, discord.File):
            await message.channel.send("The response was too long, here is a text file with the details:", file=gpt)
        else:
            await message.channel.send(gpt)

client.run(os.environ["D"])
