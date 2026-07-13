import discord
import os
import requests
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

async def query_groq(prompt, max_tokens=300):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    system_prompt = "Give short and concise answers. Be direct and to the point. "
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "system", "content": system_prompt},
                     {"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": max_tokens  # Limit response to specified max_tokens
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
    else:
        return f"❌ Error from Groq: {response.status_code} - {response.text}"

@client.event
async def on_ready():
    print(f"🤖 Bot is running as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("!ask "):
        # Example: !ask 100 What is Python?
        parts = message.content[len("!ask "):].split(" ", 1)
        if parts[0].isdigit():
            max_tokens = int(parts[0])
            prompt = parts[1] if len(parts) > 1 else ""
        else:
            max_tokens = 300
            prompt = message.content[len("!ask "):]
        
        await message.channel.send("💬 Thinking...")
        reply = await query_groq(prompt, max_tokens)
        await message.channel.send(reply)

client.run(DISCORD_TOKEN)
