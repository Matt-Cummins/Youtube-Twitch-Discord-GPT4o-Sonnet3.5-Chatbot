# YouTube Bot

A YouTube bot that interacts with the YouTube API to perform various tasks and provide information to users.

## Features

- Search for YouTube videos
- Retrieve video information
- Retrieve channel information
- Fetch METAR, TAF, and NOTAM data
- Fetch aircraft and airport information
- Fetch chart information
- Fetch weather information

## Installation

1. Clone the repository:
git clone [(https://github.com/Matt-Cummins/Youtube-Twitch-Discord-GPT4-Chatbot)]


Copy code

2. Install the required dependencies:
pip install -r requirements.txt


Copy code

3. Set up the necessary environment variables:
- `YOUTUBE_API_KEY`: Your YouTube API key
- `YOUTUBE_ACCESS_TOKEN`: Your YouTube access token
- `YOUTUBE_LIVE_CHAT_ID`: The ID of your YouTube live chat
- Add other required environment variables

## Usage

1. Run the bot:
python main.py


Copy code

2. Interact with the bot using the following commands:
- `!search <query>`: Search for YouTube videos
- `!videoinfo <video_id>`: Get information about a specific video
- `!channelinfo <channel_id>`: Get information about a specific channel
- `!metar <station_code>`: Get METAR data for a given station
- `!taf <station_code>`: Get TAF data for a given station
- `!notam <station_code>`: Get NOTAM data for a given station
- `!aircraft <aircraft_type>`: Get information about a specific aircraft type
- `!airport <airport_code>`: Get information about a specific airport
- `!chart <chart_name>`: Get information about a specific chart
- `!weather <location>`: Get weather information for a specific location

## Configuration

The bot uses a `Config` class to manage configuration variables loaded from environment variables. Here's a breakdown of the important parts:

- The `get_env_variable` static method is a helper function that retrieves the value of an environment variable. It takes the following arguments:
- `name` (str): The name of the environment variable.
- `default` (Any): The default value to return if the environment variable is not set. It defaults to `None`.
- `required` (bool): Indicates whether the environment variable is required. It defaults to `False`.

If the environment variable is required but not set, it raises a `ValueError`. Otherwise, it returns the value of the environment variable or the default value if not set.

- The `load_configuration` class method is responsible for loading various configuration values from environment variables and assigning them to class variables. It uses the `get_env_variable` method to retrieve the values. The configuration values being loaded include:
- `DISCORD_BOT_TOKEN`: The token for the Discord bot.
- `TWITCH_CLIENT_ID`: The client ID for the Twitch API.
- `TWITCH_CLIENT_SECRET`: The client secret for the Twitch API.
- `OPENAI_API_KEY`: The API key for OpenAI.
- `GOOGLE_PSE_ID`: The ID for Google Programmable Search Engine.
- `GOOGLE_PSE_API_KEY`: The API key for Google Programmable Search Engine.
- `TWITCH_BOT_NAME`: The name of the Twitch bot (defaults to 'defaultBotName').
- `TWITCH_BOT_TOKEN`: The token for the Twitch bot.
- `TWITCH_CHANNEL_NAME`: The name of the Twitch channel (defaults to 'defaultChannelName').
- `ACCESS_TOKEN`: Initialized to `None`.
- `TOKEN_EXPIRY`: Initialized to `0`.
- `YOUTUBE_API_KEY`: The API key for YouTube.
- `YOUTUBE_ACCESS_TOKEN`: The access token for YouTube.
- `YOUTUBE_LIVE_CHAT_ID`: The ID of the YouTube live chat.
- `AVWX_API_KEY`: The API key for AVWX.
- `ICAO_API_KEY`: The API key for ICAO.
- `RAPIDAPI_KEY`: The API key for RapidAPI.
- `OPENWEATHERMAP_API_KEY`: The API key for OpenWeatherMap.
- `AVIATION_EDGE_API_KEY`: The API key for Aviation Edge.
- `NAVIGRAPH_API_KEY`: The API key for Navigraph.

This configuration class provides a centralized way to load and access configuration values from environment variables. By using environment variables, sensitive information like API keys and tokens can be kept separate from the code and easily managed in different environments.

## Discord Bot

The `discord_bot.py` file sets up a Discord bot using the `discord.py` library. Here's a breakdown of the main components and functionality:

- The necessary libraries and modules are imported, including `discord`, `commands`, `aiohttp`, `asyncio`, `nltk`, `openai`, `pypresence`, and `signal`.
- Logging is set up using the `logging` module to provide detailed logs.
- The `setup_nltk()` function is called to ensure the required NLTK modules are downloaded.
- The Discord bot is set up using the `commands.Bot` class, with a specified command prefix and intents.
- Discord Rich Presence is set up using the `pypresence` library. The `update_discord_presence()` function is defined to update the bot's presence with relevant information, and the `disconnect_discord_presence()` function is defined to gracefully disconnect from Rich Presence.
- Signal handlers are set up using the `signal` module to handle graceful shutdown of the bot when receiving SIGINT or SIGTERM signals.
- Event listeners are defined using the `@bot.event` decorator:
- `on_ready()`: Triggered when the bot successfully connects to Discord. It logs a message indicating that the bot has connected.
- Command handlers are defined using the `@bot.command()` decorator:
- `metar_command()`: Fetches METAR data for a given ICAO station code using the `fetch_metar()` function (not shown in the provided code) and sends the data as a response.
- `airport_info()`: Fetches airport information for a given IATA airport code using the `get_airport_info()` function and sends the information as a response.
- `flight_info()`: Fetches flight information for a given IATA airport code using the `get_flight_info()` function and sends the information as a response.
- `notams()`: Fetches NOTAMs (Notices to Airmen) for a given IATA airport code using the `get_notams()` function and sends the NOTAMs as a response.
- `tafs()`: Fetches TAFs (Terminal Aerodrome Forecasts) for a given IATA airport code using the `get_tafs()` function and sends the TAFs as a response.
- The `run_discord_bot()` function is defined as an asynchronous function to start the Discord bot using the bot token from the configuration.

The code also includes functions for retrieving airport information, flight information, NOTAMs, and TAFs using the Aviation Edge API. The API key is obtained from the `Config` class.

The Discord Rich Presence functionality is set up to update the bot's presence with relevant information, but the actual implementation is not provided in the code.

## Main Application

The `main.py` file serves as the entry point for running multiple bots concurrently using the `asyncio` library. Here's a breakdown of what the code does:

- The necessary modules are imported:
- `asyncio`: Provides support for asynchronous programming in Python.
- `config`: Imports the `Config` class from the `config` module, which is responsible for loading configuration values.
- `discord_bot`: Imports the `run_discord_bot` function from the `discord_bot` module, which runs the Discord bot.
- `twitch_bot`: Imports the `run_twitch_bot` function from the `twitch_bot` module, which runs the Twitch bot.
- `youtube_bot`: Imports the `YouTubeBot` class and the `run_youtube_bot` function from the `youtube_bot` module, which runs the YouTube bot.
- The `main()` function is defined as an asynchronous function. It serves as the main entry point of the program.
- Inside the `main()` function:
- The `Config.load_configuration()` method is called to load the configuration values from environment variables.
- Three asynchronous tasks are created using `asyncio.create_task()`:
 - `discord_task`: Runs the Discord bot by calling the `run_discord_bot()` function.
 - `twitch_task`: Runs the Twitch bot by calling the `run_twitch_bot()` function.
 - `youtube_task`: Creates an instance of the `YouTubeBot` class with the necessary configuration values and runs the YouTube bot by calling the `run_youtube_bot()` function with the `youtube_bot` instance.
- The `asyncio.gather()` function is used to run all three tasks concurrently and wait for them to complete.
- The `if __name__ == '__main__':` block is used to ensure that the code inside it is only executed when the script is run directly (not imported as a module).
- Inside the `if` block, the `asyncio.run()` function is called with the `main()` function as its argument. This starts the event loop and runs the `main()` function asynchronously.

The `main.py` file sets up and runs three different bots (Discord bot, Twitch bot, and YouTube bot) concurrently using the `asyncio` library. The bots are defined in separate modules (`discord_bot.py`, `twitch_bot.py`, and `youtube_bot.py`), and their respective `run_` functions are called as asynchronous tasks within the `main()` function.

The `Config.load_configuration()` method is called to load the necessary configuration values from environment variables before running the bots.

By using `asyncio.gather()`, the program ensures that all three bots run concurrently and the program waits for all of them to complete before exiting.

## Twitch Bot

The `twitch_bot.py` file sets up a Twitch bot using the `twitchio` library. Here's a breakdown of the main components and functionality:

- The necessary libraries and modules are imported, including `os`, `logging`, `asyncio`, `aiohttp`, `xml.etree.ElementTree`, `requests`, `twitchio.ext.commands`, and custom modules `config` and `utils`.
- Logging is set up using the `logging` module to provide detailed logs.
- The `fetch_metar` function is defined as an asynchronous function to fetch METAR data for a given station code using the Aviation Weather API. It returns the METAR data if found, or an error message if not found or an error occurred.
- The `get_airport_info`, `get_flight_info`, `get_notams`, and `get_tafs` functions are defined to retrieve airport information, real-time flight information, NOTAMs, and TAFs, respectively, using the Aviation Edge API. They return the corresponding data if found, or `None` if not found or an error occurred.
- The `TwitchBot` class is defined, which inherits from `twitch_commands.Bot`. It represents the Twitch bot and handles the bot's functionality.
- The `__init__` method of the `TwitchBot` class initializes the bot with the necessary configuration values, such as the IRC token, client ID, client secret, bot name, command prefix, and initial channels to join.
- The `event_ready` method is an event handler that is called when the bot is ready and connected to Twitch. It logs a message indicating that the bot is ready and sends a message to the specified Twitch channel.
- The `event_message` method is an event handler that is called when a message is received in the Twitch chat. It checks if the message is a command (starts with '!') and handles it accordingly. If the message mentions the bot's name or a specific keyword, it processes the message and generates a response using the `get_response` function from the `utils` module.
- The `send_message_in_chunks` method is a helper function that sends a message to the Twitch chat in chunks to avoid exceeding the character limit. It splits the message into chunks of a specified size and sends them with a small delay to avoid rate limits.
- The `run_twitch_bot` function is defined as an asynchronous function to run the Twitch bot. It creates an instance of the `TwitchBot` class and starts the bot.

The code also includes functions for retrieving METAR data, airport information, flight information, NOTAMs, and TAFs using various APIs. The API keys are obtained from the `Config` class.

Overall, this Twitch bot interacts with the Twitch chat, handles commands, and provides responses based on user messages. It also includes functionality for retrieving aviation-related information.

## Utility Functions

The `utils.py` file contains utility functions that are used by other modules in your project. Here's a breakdown of the functions:

- `make_api_request(url, params={})`:
- This is an asynchronous function that makes API requests using the `aiohttp` library.
- It takes the `url` and optional `params` as arguments.
- It creates an `aiohttp.ClientSession` and sends a GET request to the specified URL with the provided parameters.
- If the response is successful, it returns the JSON data from the response.
- If an error occurs during the request, it logs the error and returns `None`.

- `setup_nltk()`:
- This function sets up the necessary resources for the Natural Language Toolkit (NLTK) library.
- It checks if the required resources ('punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words') are already downloaded.
- If any resource is missing, it downloads it quietly using `nltk.download()`.

- `get_continuous_chunks(text)`:
- This function extracts continuous chunks (named entities) from the given `text`.
- It tokenizes the text into words using `word_tokenize()`, tags the words with their part-of-speech using `pos_tag()`, and chunks the tagged words using `ne_chunk()`.
- It then iterates over the chunked tree and extracts the named entities (continuous chunks) from it.
- It returns a list of unique named entities found in the text.

- `perform_web_search(query)`:
- This function performs a web search using the Google Custom Search API.
- It takes the search `query` as an argument.
- It constructs the API request URL using the base URL, search engine ID, and API key from the configuration.
- It sends a GET request to the API with the search query and parameters.
- If the response is successful, it returns the JSON data from the response.
- If an HTTP error occurs or any other exception is raised, it logs the error and returns `None`.

- `format_search_results(results)`:
- This function formats the search results obtained from the `perform_web_search()` function.
- It takes the `results` JSON data as an argument.
- If the `results` are empty or do not contain an 'items' key, it returns a default message indicating no results were found.
- Otherwise, it extracts the 'snippet' field from the first three search result items and joins them with newline characters.
- It returns the formatted search results as a string.

These utility functions provide common functionality that can be used across different modules in your project. They handle tasks such as making API requests, setting up NLTK resources, extracting named entities from text, performing web searches, and formatting search results.

By separating these utility functions into a separate module, you can keep your main code cleaner and more focused on the specific functionality of each bot or module. Other modules can import and use these utility functions as needed.





## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.






Proprietary Software License Agreement

IMPORTANT: READ THIS LICENSE AGREEMENT CAREFULLY BEFORE USING THIS SOFTWARE.

    License Grant. Matthew Cummins ("Licensor") grants to the user ("Licensee") a non-exclusive, non-transferable, revocable license to use AeroStream AI ("Software") solely for Licensee's personal or internal business purposes. This license does not allow Licensee to use the Software for any other purpose, or to distribute, sell, lease, or otherwise make available the Software to third parties, except as expressly provided in this Agreement.

    Restrictions. Licensee shall not, and shall not permit any third party to, modify, adapt, translate, create derivative works from, reverse engineer, disassemble, decompile, or otherwise attempt to derive any source code from the Software. Licensee shall not use the Software in a manner that violates any applicable law or regulation.

    Ownership. The Software is the proprietary information and property of the Licensor and its licensors, protected by copyright and other intellectual property laws and treaties. Licensee does not acquire any ownership rights in the Software or its intellectual property by virtue of this License Agreement.

    No Warranty. THE SOFTWARE IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND. LICENSOR DISCLAIMS ALL WARRANTIES, WHETHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.

    Limitation of Liability. IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING BUT NOT LIMITED TO PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

    Termination. This License Agreement is effective until terminated. Licensor may terminate this License Agreement at any time if Licensee breaches any term of this License Agreement. Upon termination, Licensee shall immediately cease all use of the Software and delete all copies.

Matthew Cummins 6 Páirc na hAbhainn, Edgeworthstown, Co. Longford, N39 WK02 xbard@protonmail.com

Copyright (c) 2024 Matthew Cummins. All rights reserved.

END OF LICENSE AGREEMENT
