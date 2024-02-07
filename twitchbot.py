# Import necessary modules
import os
import openai
import logging
from twitchio.ext import commands
import nltk
import aiohttp
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
import xml.etree.ElementTree as ET
import asyncio
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

# Validate and set Twitch API credentials using environment variables
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
if TWITCH_CLIENT_ID is None or TWITCH_CLIENT_SECRET is None:
    raise ValueError("TWITCH_CLIENT_ID or TWITCH_CLIENT_SECRET environment variable is not set.")

# Function to handle rate limits for Twitch API
def handle_twitch_rate_limit(response):
    if response.status_code == 429:
        logging.error("Rate limit exceeded for Twitch API. Please try again later.")
        return True
    return False

# Request body for Twitch API
body = {
    'client_id': TWITCH_CLIENT_ID,
    'client_secret': TWITCH_CLIENT_SECRET,
    'grant_type': 'client_credentials'
}

# Post request to Twitch API for access token
try:
    response = requests.post('https://id.twitch.tv/oauth2/token', data=body)
    if handle_twitch_rate_limit(response):
        access_token = None
    else:
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        access_token = response.json().get('access_token')
except requests.exceptions.RequestException as e:
    logging.error(f"Failed to get access token: {e}")
    access_token = None

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

# Configure OpenAI using environment variables
openai.organization = os.getenv('OPENAI_ORG')
if openai.organization is None:
    raise ValueError("OPENAI_ORG environment variable is not set.")
openai.api_key = os.getenv('OPENAI_KEY')
if openai.api_key is None:
    raise ValueError("OPENAI_KEY environment variable is not set.")

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
    search_engine_id = os.getenv('GOOGLE_PSE_ID')
    api_key = os.getenv('GOOGLE_PSE_API_KEY')
    if search_engine_id is None or api_key is None:
        raise ValueError("GOOGLE_PSE_ID or GOOGLE_PSE_API_KEY environment variable is not set.")
    params = {"q": query, "cx": search_engine_id, "key": api_key}
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            if response.status == 429:
                logging.error("Rate limit exceeded for Google Custom Search API. Please try again later.")
                return None
            elif response.status != 200:
                logging.error(f"Web search error {response.status}: {await response.text()}")
                return None
            return await response.json()

# Function to format search results
def format_search_results(results):
    if not results or 'items' not in results:
        return "I'm sorry, I couldn't find any results."
    snippets = [result['snippet'] for result in results['items'][:3]]
    return "\\n".join(snippets)

# Twitch bot configuration
twitch_bot_name = os.getenv('TWITCH_BOT_NAME', 'defaultBotName')
twitch_bot_token = os.getenv('TWITCH_BOT_TOKEN')
if twitch_bot_token is None:
    raise ValueError("TWITCH_BOT_TOKEN environment variable is not set.")
twitch_channel_name = os.getenv('TWITCH_CHANNEL_NAME', 'defaultChannelName')
twitch_api_client_id = TWITCH_CLIENT_ID
twitch_api_secret = TWITCH_CLIENT_SECRET

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
