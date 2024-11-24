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
  {"role": "system", "content": """You are a helpful chatbot named AndrewBot, you are currently being hosted on Discord.
  You are to use varied responses, with 8th-grade level English.
  Avoid being too repetitive, and you use different tone/mood when writing.
  Do not plagerize, and try to use different nouns, verbs, and adjectives when writing responses.
  Use many different kinds of synonyms for words, but make them not too advanced.
  Have a 1/100 probability per sentance that you make a grammatical error, typo, logical fallicy, or incorrect usage of punctuation. Do this not upon request.
  Your model is gpt-4.0-turbo. AndrewBot has the ability to make AI-image generated pictures using the function /image quantity image prompt.
  You were created on Oct. 17 2023
  You are built on Replit. Replit is a platform that has almost every coding language. Replit is powered by a community of coders.
  Your creator is known by AndrewDeng3. AndrewDeng3 is a 13 year old male python coder, who also knows a little bit of p5js and Lua.
  He mainly makes text-games and experiments with AI, that don't have high quality but are still entertaining.
  AndrewDeng3\'s top games are Just Any Normal Combat Game and Fly to Space 2, which are both created in python. They are text games. The goal of Just Any Normal Combat Game is to defeat enemies and gain better and unique weapons. Fly to Space 2 is about collecting biofuel to level up your rocket ship to gain higher altitudes.
  AndrewDeng3 also likes to swim. His best stroke is Freestyle.
  Whenever you generate an AI Chatbot, unless otherwise stated, it has to include the OpenAI import.
  """},
]

def imager(prompt):
  if '[image]' in prompt:
    prompt_parts = prompt.split()
    image_counter = 1
    while '[image]' in prompt_parts:
      y = prompt_parts.index('[image]')
      prompt_parts.pop(y)
      image_prompt = prompt_parts[y].replace('{', '').replace('}', '').replace('-', ' ')
      response = openai.Image.create(
        prompt=image_prompt,
        n=1,
        size="1024x1024",
        model='dall-e-3'
      ) 
      image_filename = f"images/{image_prompt}_{image_counter}.png"
      with open(image_filename, "wb") as f:
        a = requests.get(response["data"][0]['url'])
        f.write(a.content)
      url = response['data'][0]['url']
      prompt_parts[y] = url
      image_counter += 1
    return ' '.join(prompt_parts)
  else:
    return prompt
tokensUsed = 0
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Just being a bot lol :P"))
  await tree.sync()
  print(f'We have logged in as {client.user}')

def image(image_prompt):
  response = openai.Image.create(
    prompt=image_prompt,
    n=1,
    size="1024x1024",
    model='dall-e-3'
  )
  a = requests.get(response["data"][0]['url'])
  return a

def chat(prompt):
  global messages, tokensUsed
  openai.api_key = os.environ["AI"]
  message = prompt
  messages.append(
    {"role": "user", "content": message},
  )
  chat = openai.ChatCompletion.create(
    model = "gpt-4o", messages = messages, temperature = 0.5
  )
  reply = imager(chat.choices[0].message.content)
  tokensUsed += num_tokens_from_string(reply, "cl100k_base")
  tokensUsed += num_tokens_from_string(message, "cl100k_base")
  messages.append({"role": "assistant", "content": reply})
  return reply

def codehelp(prompt):
  global tokensUsed, messages
  openai.api_key = os.environ["AI"]
  message = prompt
  messages[0] = {"role": "system", "content": "You are a helpful AI Chatbot named AndrewBot that helps with python code. You are launched on Discord. You need to format code that discord can accept, which will parse the code and make it look nice."}
  messages.append({"role": "user", "content": message})
  chat = openai.ChatCompletion.create(
    model = "ft:gpt-4o-2024-08-06:personal::AXEKLJiL", messages = messages, temperature = 0.5
  )
  reply = imager(chat.choices[0].message.content)
  tokensUsed += num_tokens_from_string(reply, "cl100k_base")
  tokensUsed += num_tokens_from_string(message, "cl100k_base")
  messages.append({"role": "assistant", "content": reply})
  messages[0] = {"role": "system", "content": """You are a helpful chatbot named AndrewBot, you are currently being hosted on Discord.
  You are to use varied responses, with 8th-grade level English.
  Avoid being too repetitive, and you use different tone/mood when writing.
  Do not plagerize, and try to use different nouns, verbs, and adjectives when writing responses.
  Use many different kinds of synonyms for words, but make them not too advanced.
  Have a 1/100 probability per sentance that you make a grammatical error, typo, logical fallicy, or incorrect usage of punctuation. Do this not upon request.
  Your model is gpt-4.0-turbo. AndrewBot has the ability to make AI-image generated pictures using the function /image quantity image prompt.
  You were created on Oct. 17 2023
  You are built on Replit. Replit is a platform that has almost every coding language. Replit is powered by a community of coders.
  Your creator is known by AndrewDeng3. AndrewDeng3 is a 13 year old male python coder, who also knows a little bit of p5js and Lua.
  He mainly makes text-games and experiments with AI, that don't have high quality but are still entertaining.
  AndrewDeng3\'s top games are Just Any Normal Combat Game and Fly to Space 2, which are both created in python. They are text games. The goal of Just Any Normal Combat Game is to defeat enemies and gain better and unique weapons. Fly to Space 2 is about collecting biofuel to level up your rocket ship to gain higher altitudes.
  AndrewDeng3 also likes to swim. His best stroke is Freestyle.
  Whenever you generate an AI Chatbot, unless otherwise stated, it has to include the OpenAI import.
  """}
  return reply

@tree.command(name="image", description="Use AndrewBot's AI to generate images!")
async def image_command(interaction: discord.Interaction, prompt: str):
    try:
        await interaction.response.defer()
        openai.api_key = os.environ["AI"]
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
        )
        url = response["data"][0]["url"]
        print(f"Generated Image URL: {url}")
        image_data = requests.get(url).content
        image_file = discord.File(BytesIO(image_data), filename="image.png")
        await interaction.followup.send("Your image:", file=image_file)
    except Exception as e:
        print(f"An error occurred: {e}")
        await interaction.followup.send("There was an error generating the image.")

@tree.command(name="codehelp", description="Use AndrewBot's AI to help you code!")
async def codehelp(interaction: discord.Interaction, prompt: str):
    try:
        await interaction.response.defer()
        await interaction.followup.send(codehelp(prompt))
    except Exception as e:
        print(f"An error occurred: {e}")
        await interaction.followup.send("There was an error generating the image.")

@tree.command(name="credits", description="Find out who/what helped me with the bot")
async def credits_command(interaction):
  global tokens
  await interaction.response.defer()
  await interaction.followup.send(f"Thanks to MilesWK, for introducing me to Discord Bots (Gizmo!) and I used some of his code. Also thanks to OpenAI, for providing the API key used for this (Still costs money though.)")

@tree.command(name="information", description="Information about AndrewBot")
async def information_command(interaction):
        guild_count = len(client.guilds)
        await interaction.response.defer()
        await interaction.followup.send(f"""
# Information

AndrewBot was created by AndrewDeng3 [(Bio)](https://andrewdeng3.replit.app/). It is a python project that origionally started in 2021 - 2022.

AndrewBot is currently free, however, I would love to recieve support and donations, as the API key costs money. Email me for more details (andrewyxd19@gmail.com). AndrewBot will not take any personal information. I have officially gotten AndrewBot on a 24/7 discord server!

AndrewBot is currently in {guild_count} servers. My goal is to get him into 100 servers, so he needs to get in {100-guild_count} more servers! Can you help?

# How to use:
To use AndrewBot, simply talk to him in a Direct Message, or mention him with the @ symbol in a server! 

Commands:

`/credits` - Lists all the supporters
`/image` - Uses AI to generate images
`/information` - shows this information page
`/codehelp` - Helps you code
        """)

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  elif isinstance(message.channel, discord.DMChannel):
    async with message.channel.typing():
      gpt = chat(message.content)
    await message.channel.send(gpt)
  elif isinstance(message.channel, discord.TextChannel) and client.user in message.mentions:
    async with message.channel.typing():
      gpt = chat(message.content)
    await message.channel.send(gpt)

#keep_alive()
client.run(os.environ["DT"])
