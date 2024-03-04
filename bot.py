import os
import logging
import discord
from discord.ext import commands
from twitchio.ext import commands as twitch_commands
import re
import aiohttp
import asyncio
from nltk import word_tokenize, pos_tag, ne_chunk, download
from nltk.tree import Tree
import xml.etree.ElementTree as ET
import nltk
import pyaudio
import numpy as np
import time
import json
import whisper
from whisper import transcribe
import openai
from pypresence import Presence
import signal

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

# Environment Variable Management
class Config:
    @staticmethod
    def get_env_variable(name, default=None, required=False):
        value = os.getenv(name, default)
        if required and value is None:
            raise ValueError(f"Environment variable {name} is required but not set.")
        return value

    @classmethod
    def load_configuration(cls):
        cls.DISCORD_BOT_TOKEN = cls.get_env_variable('DISCORD_BOT_TOKEN', required=True)
        cls.TWITCH_CLIENT_ID = cls.get_env_variable('TWITCH_CLIENT_ID', required=True)
        cls.TWITCH_CLIENT_SECRET = cls.get_env_variable('TWITCH_CLIENT_SECRET', required=True)
        cls.OPENAI_API_KEY = cls.get_env_variable('OPENAI_KEY', required=True)  # Corrected to match usage in the code
        cls.GOOGLE_PSE_ID = cls.get_env_variable('GOOGLE_PSE_ID', required=True)
        cls.GOOGLE_PSE_API_KEY = cls.get_env_variable('GOOGLE_PSE_API_KEY', required=True)
        cls.TWITCH_BOT_NAME = cls.get_env_variable('TWITCH_BOT_NAME', 'defaultBotName')
        cls.TWITCH_BOT_TOKEN = cls.get_env_variable('TWITCH_BOT_TOKEN', required=True)
        cls.TWITCH_CHANNEL_NAME = cls.get_env_variable('TWITCH_CHANNEL_NAME', 'defaultChannelName')
        cls.ACCESS_TOKEN = None
        cls.TOKEN_EXPIRY = 0

# Function to get a new access token
async def get_access_token():
    body = {
        'client_id': Config.TWITCH_CLIENT_ID,
        'client_secret': Config.TWITCH_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    async with aiohttp.ClientSession() as session:
        response = await session.post('https://id.twitch.tv/oauth2/token', data=body)
        if response.status == 200:
            data = await response.json()
            Config.ACCESS_TOKEN = data['access_token']
            Config.TOKEN_EXPIRY = time.time() + data['expires_in']
        else:
            logging.error("Failed to obtain access token")

# Function to refresh the access token if it has expired
async def refresh_access_token_if_needed():
    if time.time() >= Config.TOKEN_EXPIRY:
        await get_access_token()

# Asynchronous Initial Setup
async def initial_setup():
    await get_access_token()
    Config.load_configuration()
    openai.api_key = Config.OPENAI_API_KEY

# NLTK Setup
def setup_nltk():
    resources = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
    for resource in resources:
        try:
            nltk.data.find(resource)
        except LookupError:
            download(resource, quiet=True)
            
# Ensure NLTK modules are downloaded
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)

setup_nltk()  # Call the setup function for NLTK

# Set up PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

# Function to capture audio
def capture_audio():
    frames = []
    for i in range(0, int(44100 / 1024 * 5)):
        data = stream.read(1024)
        frames.append(np.frombuffer(data, dtype=np.int16))
    stream.stop_stream()
    stream.close()
    p.terminate()
    return np.concatenate(frames)

# Discord Bot Setup
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Twitch Bot Setup
twitch_bot = twitch_commands.Bot(
    irc_token=Config.TWITCH_BOT_TOKEN,
    client_id=Config.TWITCH_CLIENT_ID,
    client_secret=Config.TWITCH_CLIENT_SECRET,
    nick=Config.TWITCH_BOT_NAME,
    prefix='!',
    initial_channels=[Config.TWITCH_CHANNEL_NAME]
)

# Asynchronous API Request Handling using aiohttp
async def make_api_request(url, params={}):
    async with aiohttp.ClientSession() as session:
        try:
            logging.debug(f"Making API request to {url} with params {params}")
            async with session.get(url, params=params) as response:
                response.raise_for_status()  # Raises an HTTPError for bad responses
                data = await response.json()
                logging.debug(f"API response: {data}")
                return data
        except aiohttp.ClientError as e:
            logging.error(f"API request failed: {e}")
            return None

# Twitch Bot Setup
twitch_bot = twitch_commands.Bot(
    irc_token=Config.TWITCH_BOT_TOKEN,
    client_id=Config.TWITCH_CLIENT_ID,
    client_secret=Config.TWITCH_API_SECRET,
    nick='Your_AI_Overlord',
    prefix='!',
    initial_channels=[Config.TWITCH_CHANNEL_NAME],
    )

    # Use the new function to send the response in chunks
async def send_message_in_chunks(self, channel, message, chunk_size=490):
        for i in range(0, len(message), chunk_size):
            chunk = message[i:i+chunk_size]
            await channel.send(chunk)
            await asyncio.sleep(1)  # Wait a bit before sending the next chunk to avoid rate limits

async def event_ready(self):
        logging.info(f'Twitch bot {twitch_bot_name} is ready')
        await self.get_channel(twitch_channel_name).send(f"/me has joined {twitch_channel_name}'s channel!")

async def event_message(self, message):
        if not message.author or message.author.name.lower() == twitch_bot_name.lower():
            return
        if message.content.startswith('!'):
            await self.handle_commands(message)
            return
        if "@yourbotname" in message.content or 'yourbotname' in message.content or 'yourbotname' in message.content:
            user_message = message.content.replace("@yourbotname", "").strip()
            response = await get_response(user_message, message.author.name, 'twitch_' + message.channel.name)
            await self.send_message_in_chunks(message.channel, response)


# Shared Functions
def get_continuous_chunks(text):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
        if type(i) == Tree:
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
            current_chunk = []
        else:
            continue
    return continuous_chunk

# Global variables for bot configuration
conversation_history = {}
count = 0
names = []
custom_prompt = ''
temperature = 0.78
max_tokens = 4000  # Updated to 4000 to match the new model's output limit
top_p = 1
frequency_penalty = 1.85
presence_penalty = 1.23
promptbackup = ''

# Initial bot character description
initial_prompt = "You are a slightly sarcastic Artificial Intelligence chatbot..."

# Function to check if a message is a search query
def is_search_query(message):
    message = message.lower()
    return any(message.startswith(phrase) for phrase in search_phrases)

# Function to extract continuous chunks (named entities) from text
def get_continuous_chunks(text):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
        if isinstance(i, Tree):
            current_chunk.append(" ".join([token for token, _ in i.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
            current_chunk = []
    return continuous_chunk

# Function to perform web search
def perform_web_search(query):
    base_url = "https://www.googleapis.com/customsearch/v1"
    search_engine_id = os.getenv('GOOGLE_PSE_ID')
    api_key = os.getenv('GOOGLE_PSE_API_KEY')
    params = {
        "q": query,
        "cx": search_engine_id,
        "key": api_key,
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        return None

# Function to format search results
def format_search_results(results):
    if not results or 'items' not in results:
        return "I'm sorry, I couldn't find any results."
    snippets = [result['snippet'] for result in results['items'][:3]]
    return "\\n".join(snippets)

# Function to get a response based on the user's message
def get_response(user_message, username, channel_id):
    logging.info(f"Processing user message: {user_message}")
    named_entities = get_continuous_chunks(user_message)
    response = ""
    if named_entities:
        search_query = " ".join(named_entities)
        response = f"I see you're interested in {search_query}. Here's what I found:"
        search_results = perform_web_search(search_query)
        search_summary = format_search_results(search_results)
        response += f"\\n{search_summary}"
    if channel_id not in conversation_history:
        conversation_history[channel_id] = initial_prompt
    if user_message.endswith("?"):
        search_results = perform_web_search(user_message)
        search_summary = format_search_results(search_results)
        conversation_history[channel_id] += f"\\nBased on my research, here's what I found:\\n{search_summary}"
    else:
        user_prompt = f"{username} asks: {user_message}"
        conversation_history[channel_id] += f"\\n{user_prompt}\\nAssistant responds:"
    try:
        openai_response = openai.ChatCompletion.create(
            model="gpt-4-0125-preview",  # Updated to the new model
            messages=[
                {"role": "system", "content": conversation_history[channel_id]},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        response_text = openai_response.choices[0].message['content'].strip()
        conversation_history[channel_id] += f"\\n{response_text}"
        return response_text
    except Exception as e:
        logging.error(f"An error occurred while calling OpenAI API: {e}")
        return "Sorry, I am currently experiencing technical difficulties. Please try again later."

# Function to send message in chunks
async def send_message_in_chunks(channel, message, chunk_size=490):
    for i in range(0, len(message), chunk_size):
        chunk = message[i:i+chunk_size]
        await channel.send(chunk)
        await asyncio.sleep(1)  # Wait a bit before sending the next chunk to avoid rate limits

# Initialize the Discord bot with command prefix
bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())

# Function to fetch METAR data asynchronously
async def fetch_metar(station_code):
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
        
# Function to get airport information
def get_airport_info(airport_code):
    url = f'https://aviation-edge.com/v2/public/airportDatabase?key={aviation_edge_api_key}&codeIataAirport={airport_code}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch airport info: {response.status_code}")
        return None

# Function to get real-time flight information
def get_flight_info(airport_code):
    url = f'https://aviation-edge.com/v2/public/flights?key={aviation_edge_api_key}&arrIata={airport_code}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch flight info: {response.status_code}")
        return None

# Function to get NOTAMs
def get_notams(airport_code):
    url = f'https://aviation-edge.com/v2/public/notams?key={aviation_edge_api_key}&codeIataAirport={airport_code}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch NOTAMs: {response.status_code}")
        return None

# Function to get TAFs
def get_tafs(airport_code):
    url = f'https://aviation-edge.com/v2/public/weather?key={aviation_edge_api_key}&codeIataAirport={airport_code}&type=taf'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch TAFs: {response.status_code}")
        return None

# Discord bot commands for fetching and displaying airport information, flight information, NOTAMs, and TAFs
@bot.command(name='airportinfo')
async def airport_info(ctx, airport_code: str):
    info = get_airport_info(airport_code)
    if info:
        await ctx.send(json.dumps(info, indent=2))
    else:
        await ctx.send("Airport information not found.")

@bot.command(name='flightinfo')
async def flight_info(ctx, airport_code: str):
    info = get_flight_info(airport_code)
    if info:
        await ctx.send(json.dumps(info, indent=2))
    else:
        await ctx.send("Flight information not found.")

@bot.command(name='notams')
async def notams(ctx, airport_code: str):
    info = get_notams(airport_code)
    if info:
        await ctx.send(json.dumps(info, indent=2))
    else:
        await ctx.send("NOTAMs not found.")

@bot.command(name='tafs')
async def tafs(ctx, airport_code: str):
    info = get_tafs(airport_code)
    if info:
        await ctx.send(json.dumps(info, indent=2))
    else:
        await ctx.send("TAFs not found.")
        
# Command to fetch METAR data
@bot.command(name='metar')
async def metar_command(ctx, *, station_code: str):
    station_code = station_code.upper().strip()
    if re.match(r'\b[A-Z]{4}\b', station_code):
        metar_data = await fetch_metar(station_code)
        await ctx.send(metar_data)
    else:
        await ctx.send("Please provide a valid ICAO airport code.")
        
# Event listener for when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')



# Discord Rich Presence setup
client_id = 'YOUR_CLIENT_ID'  # Replace with your Discord application's client ID
RPC = Presence(client_id)
RPC.connect()

def update_discord_presence():
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
        
# At appropriate points in your application, call update_discord_presence() to update the user's Discord status
# This is just an example, you should call this in response to actual events in your application
update_discord_presence()

# Remember to include logic for gracefully disconnecting from Discord Rich Presence when your application closes
def disconnect_discord_presence():
    try:
        RPC.close()
        logging.info("Disconnected from Discord Rich Presence successfully.")
    except Exception as e:
        logging.error(f"Failed to disconnect from Discord Rich Presence: {e}")

# Ensure graceful shutdown
def signal_handler(sig, frame):
    logging.info('Shutdown signal received. Disconnecting from Discord Rich Presence...')
    disconnect_discord_presence()
    # Perform any other cleanup tasks here
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
# Run the bots
async def main():
    discord_task = asyncio.create_task(discord_bot.start(Config.DISCORD_BOT_TOKEN))
    twitch_task = asyncio.create_task(twitch_bot.start())
    await asyncio.gather(discord_task, twitch_task)

if __name__ == '__main__':
    asyncio.run(main())
