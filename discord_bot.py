import os
import logging
import discord
from discord.ext import commands
import aiohttp
import asyncio
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
import nltk
import openai
from pypresence import Presence
import signal
from config import Config
from utils import setup_nltk, make_api_request, get_continuous_chunks, perform_web_search, format_search_results

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

# Ensure NLTK modules are downloaded
setup_nltk()

# Discord Bot Setup
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Discord Rich Presence setup
client_id = Config.DISCORD_CLIENT_ID  # Replace with your Discord application's client ID
RPC = Presence(client_id)
RPC.connect()

def get_airport_info(airport_code):
    """
    Retrieve airport information for a given airport code.

    Args:
        airport_code (str): The IATA airport code.

    Returns:
        dict: The airport information as a dictionary, or None if not found.
    """
    url = f'https://aviation-edge.com/v2/public/airportDatabase?key={Config.AVIATION_EDGE_API_KEY}&codeIataAirport={airport_code}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch airport info: {response.status_code}")
        return None

def get_flight_info(airport_code):
    """
    Retrieve real-time flight information for a given airport code.

    Args:
        airport_code (str): The IATA airport code.

    Returns:
        dict: The flight information as a dictionary, or None if not found.
    """
    url = f'https://aviation-edge.com/v2/public/flights?key={Config.AVIATION_EDGE_API_KEY}&arrIata={airport_code}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch flight info: {response.status_code}")
        return None

def get_notams(airport_code):
    """
    Retrieve NOTAMs (Notices to Airmen) for a given airport code.

    Args:
        airport_code (str): The IATA airport code.

    Returns:
        dict: The NOTAMs as a dictionary, or None if not found.
    """
    url = f'https://aviation-edge.com/v2/public/notams?key={Config.AVIATION_EDGE_API_KEY}&codeIataAirport={airport_code}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch NOTAMs: {response.status_code}")
        return None

def get_tafs(airport_code):
    """
    Retrieve TAFs (Terminal Aerodrome Forecasts) for a given airport code.

    Args:
        airport_code (str): The IATA airport code.

    Returns:
        dict: The TAFs as a dictionary, or None if not found.
    """
    url = f'https://aviation-edge.com/v2/public/weather?key={Config.AVIATION_EDGE_API_KEY}&codeIataAirport={airport_code}&type=taf'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch TAFs: {response.status_code}")
        return None

def update_discord_presence():
    """
    Update the Discord Rich Presence status.
    """
    try:
        # Example: Update Discord Rich Presence to reflect user's current activity
        RPC.update(state="Engaged in Activity",
                   details="Participating in Online Event",
                   start=int(time.time()),  # Current time as start timestamp
                   large_image="your_large_image_key",  # Replace with your image key
                   large_text="Activity Details",
                   small_image="your_small_image_key",  # Replace with your image key
                   small_text="More Details",
                   party_id="some_unique_party_id",  # Unique ID for the user's party/group
                   party_size=[1, 5],  # Example: user's party size and max size
                   join_secret="some_join_secret")  # Secret for joining the user's party/group
        logging.info("Discord Rich Presence updated successfully.")
    except Exception as e:
        logging.error(f"Failed to update Discord Rich Presence: {e}")

def disconnect_discord_presence():
    """
    Disconnect from Discord Rich Presence.
    """
    try:
        RPC.close()
        logging.info("Disconnected from Discord Rich Presence successfully.")
    except Exception as e:
        logging.error(f"Failed to disconnect from Discord Rich Presence: {e}")

def signal_handler(sig, frame):
    """
    Signal handler for graceful shutdown.
    """
    logging.info('Shutdown signal received. Disconnecting from Discord Rich Presence...')
    disconnect_discord_presence()
    # Perform any other cleanup tasks here
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@bot.event
async def on_ready():
    """
    Event listener for when the bot is ready.
    """
    print(f'{bot.user.name} has connected to Discord!')
    logging.info(f'Logged in as {bot.user}')

@bot.command(name='metar')
async def metar_command(ctx, *, station_code: str):
    """
    Command to fetch METAR data for a given station code.

    Args:
        ctx: The command context.
        station_code (str): The ICAO station code.
    """
    try:
        station_code = station_code.upper().strip()
        if re.match(r'\b[A-Z]{4}\b', station_code):
            metar_data = await fetch_metar(station_code)
            await ctx.send(metar_data)
        else:
            await ctx.send("Please provide a valid ICAO airport code.")
    except Exception as e:
        logging.error(f"Error in metar command: {e}")
        await ctx.send("An error occurred while processing the command.")

@bot.command(name='airportinfo')
async def airport_info(ctx, airport_code: str):
    """
    Command to fetch and display airport information for a given airport code.

    Args:
        ctx: The command context.
        airport_code (str): The IATA airport code.
    """
    try:
        info = get_airport_info(airport_code)
        if info:
            await ctx.send(json.dumps(info, indent=2))
        else:
            await ctx.send("Airport information not found.")
    except Exception as e:
        logging.error(f"Error in airportinfo command: {e}")
        await ctx.send("An error occurred while processing the command.")

@bot.command(name='flightinfo')
async def flight_info(ctx, airport_code: str):
    """
    Command to fetch and display flight information for a given airport code.

    Args:
        ctx: The command context.
        airport_code (str): The IATA airport code.
    """
    try:
        info = get_flight_info(airport_code)
        if info:
            await ctx.send(json.dumps(info, indent=2))
        else:
            await ctx.send("Flight information not found.")
    except Exception as e:
        logging.error(f"Error in flightinfo command: {e}")
        await ctx.send("An error occurred while processing the command.")

@bot.command(name='notams')
async def notams(ctx, airport_code: str):
    """
    Command to fetch and display NOTAMs for a given airport code.

    Args:
        ctx: The command context.
        airport_code (str): The IATA airport code.
    """
    try:
        info = get_notams(airport_code)
        if info:
            await ctx.send(json.dumps(info, indent=2))
        else:
            await ctx.send("NOTAMs not found.")
    except Exception as e:
        logging.error(f"Error in notams command: {e}")
        await ctx.send("An error occurred while processing the command.")

@bot.command(name='tafs')
async def tafs(ctx, airport_code: str):
    """
    Command to fetch and display TAFs for a given airport code.

    Args:
        ctx: The command context.
        airport_code (str): The IATA airport code.
    """
    try:
        info = get_tafs(airport_code)
        if info:
            await ctx.send(json.dumps(info, indent=2))
        else:
            await ctx.send("TAFs not found.")
    except Exception as e:
        logging.error(f"Error in tafs command: {e}")
        await ctx.send("An error occurred while processing the command.")

async def run_discord_bot():
    """
    Run the Discord bot.
    """
    await bot.start(Config.DISCORD_BOT_TOKEN)

async def run_discord_bot():
    """
    Run the Discord bot.
    """
    await bot.start(Config.DISCORD_BOT_TOKEN)
