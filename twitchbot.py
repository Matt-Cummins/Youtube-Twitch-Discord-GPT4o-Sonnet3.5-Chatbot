import time
import os
import openai
import logging
from twitchio.ext import commands
import nltk
import aiohttp
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
import asyncio
import requests
import pyaudio
import numpy as np
from whisper import transcribe

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

# Example of detailed logging in an API request function
def make_api_request(url, params):
    try:
        logging.debug(f"Making API request to {url} with params {params}")
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        logging.debug(f"API response: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None

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
        cls.TWITCH_CLIENT_ID = cls.get_env_variable('TWITCH_CLIENT_ID', required=True)
        cls.TWITCH_CLIENT_SECRET = cls.get_env_variable('TWITCH_CLIENT_SECRET', required=True)
        cls.OPENAI_ORG = cls.get_env_variable('OPENAI_ORG', required=True)
        cls.OPENAI_KEY = cls.get_env_variable('OPENAI_KEY', required=True)
        cls.GOOGLE_PSE_ID = cls.get_env_variable('GOOGLE_PSE_ID', required=True)
        cls.GOOGLE_PSE_API_KEY = cls.get_env_variable('GOOGLE_PSE_API_KEY', required=True)
        cls.TWITCH_BOT_NAME = cls.get_env_variable('TWITCH_BOT_NAME', 'defaultBotName')
        cls.TWITCH_BOT_TOKEN = cls.get_env_variable('TWITCH_BOT_TOKEN', required=True)
        cls.TWITCH_CHANNEL_NAME = cls.get_env_variable('TWITCH_CHANNEL_NAME', 'defaultChannelName')
        cls.ACCESS_TOKEN = None
        cls.TOKEN_EXPIRY = 0

# Load configuration
Config.load_configuration()

# Function to handle rate limits with retry for synchronous requests
def handle_rate_limit_with_retry(request_func, params, max_retries=3, initial_wait=1):
    retry_count = 0
    while retry_count < max_retries:
        response = request_func(params)
        if response.status_code != 429:
            return response
        logging.error(f"Rate limit exceeded. Retry attempt {retry_count + 1} of {max_retries}.")
        time.sleep(initial_wait * (2 ** retry_count))  # Corrected exponential backoff
        retry_count += 1
    logging.error("Max retries exceeded for rate limit handling.")
    return None

# Function to handle rate limits with retry for asynchronous requests
async def handle_rate_limit_with_retry_async(request_func, params, max_retries=3, initial_wait=1):
    retry_count = 0
    while retry_count < max_retries:
        response = await request_func(params)
        if response.status != 429:
            return response
        logging.error(f"Rate limit exceeded. Retry attempt {retry_count + 1} of {max_retries}.")
        await asyncio.sleep(initial_wait * (2 ** retry_count))  # Corrected exponential backoff
        retry_count += 1
    logging.error("Max retries exceeded for rate limit handling.")
    return None

# Function to get a new access token
def get_access_token():
    body = {
        'client_id': Config.TWITCH_CLIENT_ID,
        'client_secret': Config.TWITCH_CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post('https://id.twitch.tv/oauth2/token', data=body)
    if response.status_code == 200:
        data = response.json()
        Config.ACCESS_TOKEN = data['access_token']  # Calculate the expiry time as current time + expires_in seconds
        Config.TOKEN_EXPIRY = time.time() + data['expires_in']
    else:
        logging.error("Failed to obtain access token")

# Function to refresh the access token if it has expired
def refresh_access_token_if_needed():
    if time.time() >= Config.TOKEN_EXPIRY:
        get_access_token()

# Ensure get_access_token is called during initial setup
get_access_token()

# Function to ensure necessary NLTK modules are downloaded
def setup_nltk():
    resources = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
    for resource in resources:
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.download(resource, quiet=True)

# Call the setup function for NLTK
setup_nltk()

# Define search phrases
search_phrases = ["search for", "find", "look up", "what is", "who is", "tell me about"]

# Function to check if a message is a search query
def is_search_query(message):
    message = message.lower()
    return any(message.startswith(phrase) for phrase in search_phrases)

# Set up PyAudio
p = pyaudio.PyAudio()

# Start a new stream
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

# Function to capture audio
def capture_audio():
    frames = []

    # Capture audio for a certain duration (e.g., 5 seconds)
    for i in range(0, int(44100 / 1024 * 5)):
        data = stream.read(1024)
        frames.append(np.frombuffer(data, dtype=np.int16))

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Terminate the PortAudio interface
    p.terminate()

    return np.concatenate(frames)

# Function to transcribe audio
def transcribe_audio(audio):
    # Convert the numpy array to a list
    audio_list = audio.tolist()

    # Use the Whisper ASR system to transcribe the audio
    transcription = transcribe(audio_list)

    return transcription

# Configure OpenAI using environment variables
openai.organization = Config.OPENAI_ORG
openai.api_key = Config.OPENAI_KEY

# Global variables for bot configuration
conversation_history = {}
temperature = 0.78
max_tokens = 4000
top_p = 1
frequency_penalty = 1.85
presence_penalty = 1.23

# Initial bot character description
initial_prompt = "You are a slightly sarcastic Artificial Intelligence chatbot..."

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

# Asynchronous function to perform web search with rate limit handling
async def perform_web_search_async(query):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'cx': Config.GOOGLE_PSE_ID,
        'key': Config.GOOGLE_PSE_API_KEY
    }
    async with aiohttp.ClientSession() as session:
        response = await handle_rate_limit_with_retry_async(session.get, {'url': base_url, 'params': params})
        if response is not None and response.status == 200:
            return await response.json()
        else:
            return None

# Function to format search results
def format_search_results(results):
    if not results or 'items' not in results:
        return "I'm sorry, I couldn't find any results."
    snippets = [result['snippet'] for result in results['items'][:3]]
    return "\\n".join(snippets)

# Twitch bot configuration
twitch_bot_name = Config.TWITCH_BOT_NAME
twitch_bot_token = Config.TWITCH_BOT_TOKEN
twitch_channel_name = Config.TWITCH_CHANNEL_NAME
twitch_api_client_id = Config.TWITCH_CLIENT_ID
twitch_api_secret = Config.TWITCH_CLIENT_SECRET

# Twitch bot class
class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(
            irc_token=twitch_bot_token,
            client_id=twitch_api_client_id,
            client_secret=twitch_api_secret,
            nick=twitch_bot_name,
            prefix='!',
            initial_channels=[twitch_channel_name],
            token=twitch_bot_token,
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

# Main function
async def main():
    bot = TwitchBot()
    await bot.start()

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
