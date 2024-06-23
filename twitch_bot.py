# twitch_bot.py
import os
import logging
import asyncio
import aiohttp
import xml.etree.ElementTree as ET
import requests
from twitchio.ext import commands as twitch_commands
from config import Config
from utils import get_response

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

async def fetch_metar(station_code):
    """
    Fetch METAR data asynchronously for a given station code.

    Args:
        station_code (str): The ICAO station code.

    Returns:
        str: The METAR data if found, or an error message if not found or an error occurred.
    """
    url = f"https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&stationString={station_code}&hoursBeforeNow=1"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    xml_data = await response.text()
                    root = ET.fromstring(xml_data)
                    metar_element = root.find(".//METAR/raw_text")
                    if metar_element is not None:
                        return metar_element.text
                    else:
                        return "No METAR data found."
                else:
                    return f"Failed to fetch METAR data, HTTP status: {response.status}"
        except Exception as e:
            logging.exception(f"Error fetching METAR data for {station_code}: {e}")
            return "Failed to fetch METAR data due to an error."

def get_airport_info(airport_code):
    """
    Get airport information for a given airport code.

    Args:
        airport_code (str): The IATA airport code.

    Returns:
        dict: The airport information if found, or None if not found or an error occurred.
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
    Get real-time flight information for a given airport code.

    Args:
        airport_code (str): The IATA airport code.

    Returns:
        dict: The flight information if found, or None if not found or an error occurred.
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
    Get NOTAMs (Notices to Airmen) for a given airport code.

    Args:
        airport_code (str): The IATA airport code.

    Returns:
        dict: The NOTAMs if found, or None if not found or an error occurred.
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
    Get TAFs (Terminal Aerodrome Forecasts) for a given airport code.

    Args:
        airport_code (str): The IATA airport code.

    Returns:
        dict: The TAFs if found, or None if not found or an error occurred.
    """
    url = f'https://aviation-edge.com/v2/public/weather?key={Config.AVIATION_EDGE_API_KEY}&codeIataAirport={airport_code}&type=taf'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch TAFs: {response.status_code}")
        return None

class TwitchBot(twitch_commands.Bot):
    """
    A Twitch bot that interacts with the Twitch chat and handles commands.
    """
    def __init__(self):
        super().__init__(
            irc_token=Config.TWITCH_BOT_TOKEN,
            client_id=Config.TWITCH_CLIENT_ID,
            client_secret=Config.TWITCH_CLIENT_SECRET,
            nick=Config.TWITCH_BOT_NAME,
            prefix='!',
            initial_channels=[Config.TWITCH_CHANNEL_NAME]
        )

    async def event_ready(self):
        """
        Event handler for when the bot is ready and connected to Twitch.
        """
        logging.info(f'Twitch bot {self.nick} is ready')
        await self.get_channel(Config.TWITCH_CHANNEL_NAME).send(f"/me has joined {Config.TWITCH_CHANNEL_NAME}'s channel!")

    async def event_message(self, message):
        """
        Event handler for when a message is received in the Twitch chat.

        Args:
            message (twitchio.Message): The message object received from Twitch.
        """
        if message.echo:
            return

        if message.content.startswith('!'):
            await self.handle_commands(message)
            return

        if any(name in message.content.lower() for name in [self.nick.lower(), 'yourbotname']):
            user_message = message.content.replace(self.nick, "").replace("yourbotname", "").strip()
            response = await get_response(user_message, message.author.name, 'twitch_' + message.channel.name)
            await self.send_message_in_chunks(message.channel, response)

    async def send_message_in_chunks(self, channel, message, chunk_size=490):
        """
        Send a message to the Twitch chat in chunks to avoid exceeding the character limit.

        Args:
            channel (twitchio.Channel): The Twitch channel to send the message to.
            message (str): The message to send.
            chunk_size (int): The maximum number of characters per chunk (default: 490).
        """
        for i in range(0, len(message), chunk_size):
            chunk = message[i:i+chunk_size]
            await channel.send(chunk)
            await asyncio.sleep(1)  # Wait a bit before sending the next chunk to avoid rate limits

async def run_twitch_bot():
    """
    Run the Twitch bot.
    """
    twitch_bot = TwitchBot()
    await twitch_bot.start()
