from discord.ext import commands
import discord
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot setup
bot = commands.Bot(command_prefix='!', intents=intents)

# Configuration
INTRO_CHANNEL = "💼general"
UNVERIFIED_ROLE = "Unverified"
VERIFIED_ROLE = "Verified"
MOD_ROLE = "C-suite"

# High-signal keywords and intro-like phrases
signal_keywords = [
    "founder", "building", "startup", "intern", "ai", "artificial intelligence", "ml", "machine learning",
    "engineering", "csun", "vc", "investing", "hustling", "launched", "operator", "automation"
]
intro_phrases = ["i'm", "i am", "my name is", "csun", "major", "studying", "building"]

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Jonathan Sher is online and scanning introductions.")
    channel = discord.utils.get(bot.get_all_channels(), name=INTRO_CHANNEL)
    if channel:
        print(f"🔍 Scanning last 100 messages in #{INTRO_CHANNEL}...")
        async for message in channel.history(limit=100):
            if message.author == bot.user:
                continue
            content = message.content.lower()
            if any(keyword in content for keyword in signal_keywords) or any(phrase in content for phrase in intro_phrases):
                await message.add_reaction("✅")
                verified_role = discord.utils.get(message.guild.roles, name=VERIFIED_ROLE)
                unverified_role = discord.utils.get(message.guild.roles, name=UNVERIFIED_ROLE)
                if verified_role and verified_role not in message.author.roles:
                    await message.author.add_roles(verified_role)
                    await channel.send(f"(Backfill) Welcome {message.author.mention} — verified as an operator. 🧠")
                if unverified_role and unverified_role in message.author.roles:
                    await message.author.remove_roles(unverified_role)

# Event: New member joins
@bot.event
async def on_member_join(member):
    unverified_role = discord.utils.get(member.guild.roles, name=UNVERIFIED_ROLE)
    if unverified_role:
        await member.add_roles(unverified_role)
    try:
        await member.send(
            "👋 Welcome to LA Operators Club.\n\n"
            "Please introduce yourself in `#💼general` with:\n"
            "1. Name, School & Year\n2. LinkedIn\n3. What you're building or learning\n\n"
            "Once verified, you'll unlock the rest of the community."
        )
    except discord.Forbidden:
        print(f"Couldn't DM {member.name}")

    welcome_channel = discord.utils.get(member.guild.text_channels, name=INTRO_CHANNEL)
    if welcome_channel:
        await welcome_channel.send(
            f"👋 Welcome {member.mention} to LA Operators Club. Drop an intro: what you're building, studying, or scaling — and we’ll unlock the rest. 💼"
        )

# Event: New messages in intro channel
@bot.event
async def on_message(message):
    if message.author == bot.user or message.channel.name != INTRO_CHANNEL:
        return

    content = message.content.lower()
    if any(keyword in content for keyword in signal_keywords) or any(phrase in content for phrase in intro_phrases):
        await message.add_reaction("✅")
        verified_role = discord.utils.get(message.guild.roles, name=VERIFIED_ROLE)
        unverified_role = discord.utils.get(message.guild.roles, name=UNVERIFIED_ROLE)

        if verified_role and verified_role not in message.author.roles:
            await message.author.add_roles(verified_role)
            await message.channel.send(f"Welcome {message.author.mention} — verified as an operator. 💰💰💰")

        if unverified_role and unverified_role in message.author.roles:
            await message.author.remove_roles(unverified_role)

    await bot.process_commands(message)

# Run bot
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("No Discord token found. Please set the DISCORD_TOKEN environment variable.")
bot.run(TOKEN)
