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
    ```bash
    git clone https://github.com/your-username/your-repo.git
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up the necessary environment variables:
    - `YOUTUBE_API_KEY`: Your YouTube API key
    - `YOUTUBE_ACCESS_TOKEN`: Your YouTube access token
    - `YOUTUBE_LIVE_CHAT_ID`: The ID of your YouTube live chat
    - Add other required environment variables as mentioned in the configuration section

## Usage

1. Run the bot:
    ```bash
    python main.py
    ```

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

## License

Creative Commons Attribution 4.0 International Public License

By exercising the Licensed Rights (defined below), You accept and agree to be bound by the terms and conditions of this Creative Commons Attribution 4.0 International Public License ("Public License"). To the extent this Public License may be interpreted as a contract, You are granted the Licensed Rights in consideration of Your acceptance of these terms and conditions, and the Licensor grants You such rights in consideration of benefits the Licensor receives from making the Licensed Material available under these terms and conditions.

Section 1 -- Definitions.

a. Adapted Material means material subject to Copyright and Similar Rights that is derived from or based upon the Licensed Material and in which the Licensed Material is translated, altered, arranged, transformed, or otherwise modified in a manner requiring permission under the Copyright and Similar Rights held by the Licensor. For purposes of this Public License, where the Licensed Material is a musical work, performance, or sound recording, Adapted Material is always produced where the Licensed Material is synched in timed relation with a moving image.

b. Adapter's License means the license You apply to Your Copyright and Similar Rights in Your contributions to Adapted Material in accordance with the terms and conditions of this Public License.

c. Copyright and Similar Rights means copyright and/or similar rights closely related to copyright including, without limitation, performance, broadcast, sound recording, and Sui Generis Database Rights, without regard to how the rights are labeled or categorized. For purposes of this Public License, the rights specified in Section 2(b)(1)-(2) are not Copyright and Similar Rights.

d. Effective Technological Measures means those measures that, in the absence of proper authority, may not be circumvented under laws fulfilling obligations under Article 11 of the WIPO Copyright Treaty adopted on December 20, 1996, and/or similar international agreements.

e. Exceptions and Limitations means fair use, fair dealing, and/or any other exception or limitation to Copyright and Similar Rights that applies to Your use of the Licensed Material.

f. Licensed Material means the artistic or literary work, database, or other material to which the Licensor applied this Public License.

g. Licensed Rights means the rights granted to You subject to the terms and conditions of this Public License, which are limited to all Copyright and Similar Rights that apply to Your use of the Licensed Material and that the Licensor has authority to license.

h. Licensor means the individual(s) or entity(ies) granting rights under this Public License.

i. Share means to provide material to the public by any means or process that requires permission under the Licensed Rights, such as reproduction, public display, public performance, distribution, dissemination, communication, or importation, and to make material available to the public including in ways that members of the public may access the material from a place and at a time individually chosen by them.

j. Sui Generis Database Rights means rights other than copyright resulting from Directive 96/9/EC of the European Parliament and of the Council of 11 March 1996 on the legal protection of databases, as amended and/or succeeded, as well as other essentially equivalent rights anywhere in the world.

k. You means the individual or entity exercising the Licensed Rights under this Public License. Your has a corresponding meaning.

Section 2 -- Scope.

a. License grant.

   1. Subject to the terms and conditions of this Public License,
      the Licensor hereby grants You a worldwide, royalty-free,
      non-sublicensable, non-exclusive, irrevocable license to
      exercise the Licensed Rights in the Licensed Material to:

        a. reproduce and Share the Licensed Material, in whole or
           in part; and

        b. produce, reproduce, and Share Adapted Material.

   2. Exceptions and Limitations. For the avoidance of doubt, where
      Exceptions and Limitations apply to Your use, this Public
      License does not apply, and You do not need to comply with
      its terms and conditions.

   3. Term. The term of this Public License is specified in Section
      6(a).

   4. Media and formats; technical modifications allowed. The
      Licensor authorizes You to exercise the Licensed Rights in
      all media and formats whether now known or hereafter created,
      and to make technical modifications necessary to do so. The
      Licensor waives and/or agrees not to assert any right or
      authority to forbid You from making technical modifications
      necessary to exercise the Licensed Rights, including
      technical modifications necessary to circumvent Effective
      Technological Measures. For purposes of this Public License,
      simply making modifications authorized by this Section 2(a)
      (4) never produces Adapted Material.

   5. Downstream recipients.

        a. Offer from the Licensor -- Licensed Material. Every
           recipient of the Licensed Material automatically
           receives an offer from the Licensor to exercise the
           Licensed Rights under the terms and conditions of this
           Public License.

        b. No downstream restrictions. You may not offer or impose
           any additional or different terms or conditions on, or
           apply any Effective Technological Measures to, the
           Licensed Material if doing so restricts exercise of the
           Licensed Rights by any recipient of the Licensed
           Material.

   6. No endorsement. Nothing in this Public License constitutes or
      may be construed as permission to assert or imply that You
      are, or that Your use of the Licensed Material is, connected
      with, or sponsored, endorsed, or granted official status by,
      the Licensor or others designated to receive attribution as
      provided in Section 3(a)(1)(A)(i).

b. Other rights.

   1. Moral rights, such as the right of integrity, are not
      licensed under this Public License, nor are publicity,
      privacy, and/or other similar personality rights; however, to
      the extent possible, the Licensor waives and/or agrees not to
      assert any such rights held by the Licensor to the limited
      extent necessary to allow You to exercise the Licensed
      Rights, but not otherwise.

   2. Patent and trademark rights are not licensed under this
      Public License.

   3. To the extent possible, the Licensor waives any right to
      collect royalties from You for the exercise of the Licensed
      Rights, whether directly or through a collecting society
      under any voluntary or waivable statutory or compulsory
      licensing scheme. In all other cases the Licensor expressly
      reserves any right to collect such royalties.

Section 3 -- License Conditions.

Your exercise of the Licensed Rights is expressly made subject to the following conditions.

a. Attribution.

   1. If You Share the Licensed Material (including in modified
      form), You must:

        a. retain the following if it is supplied by the Licensor
           with the Licensed Material:

             i. identification of the creator(s) of the Licensed
                Material and any others designated to receive
                attribution, in any reasonable manner requested by
                the Licensor (including by pseudonym if
                designated);

            ii. a copyright notice;

           iii. a notice that refers to this Public License;

            iv. a notice that refers to the disclaimer of
                warranties;

             v. a URI or hyperlink to the Licensed Material to the
                extent reasonably practicable;

        b. indicate if You modified the Licensed Material and
           retain an indication of any previous modifications; and

        c. indicate the Licensed Material is licensed under this
           Public License, and include the text of, or the URI or
           hyperlink to, this Public License.

   2. You may satisfy the conditions in Section 3(a)(1) in any
      reasonable manner based on the medium, means, and context in
      which You Share the Licensed Material. For example, it may be
      reasonable to satisfy the conditions by providing a URI or
      hyperlink to a resource that includes the required
      information.

   3. If requested by the Licensor, You must remove any of the
      information required by Section 3(a)(1)(A) to the extent
      reasonably practicable.

   4. If You Share Adapted Material You produce, the Adapter's
      License You apply must not prevent recipients of the Adapted
      Material from complying with this Public License.

Section 4 -- Sui Generis Database Rights.

Where the Licensed Rights include Sui Generis Database Rights that apply to Your use of the Licensed Material:

a. for the avoidance of doubt, Section 2(a)(1) grants You the right to extract, reuse, reproduce, and Share all or a substantial portion of the contents of the database;

b. if You include all or a substantial portion of the database contents in a database in which You have Sui Generis Database Rights, then the database in which You have Sui Generis Database Rights (but not its individual contents) is Adapted Material; and

c. You must comply with the conditions in Section 3(a) if You Share all or a substantial portion of the contents of the database.

For the avoidance of doubt, this Section 4 supplements and does not replace Your obligations under this Public License where the Licensed Rights include other Copyright and Similar Rights.

Section 5 -- Disclaimer of Warranties and Limitation of Liability.

a. UNLESS OTHERWISE SEPARATELY UNDERTAKEN BY THE LICENSOR, TO THE EXTENT POSSIBLE, THE LICENSOR OFFERS THE LICENSED MATERIAL AS-IS AND AS-AVAILABLE, AND MAKES NO REPRESENTATIONS OR WARRANTIES OF ANY KIND CONCERNING THE LICENSED MATERIAL, WHETHER EXPRESS, IMPLIED, STATUTORY, OR OTHER. THIS INCLUDES, WITHOUT LIMITATION, WARRANTIES OF TITLE, MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, ABSENCE OF LATENT OR OTHER DEFECTS, ACCURACY, OR THE PRESENCE OR ABSENCE OF ERRORS, WHETHER OR NOT KNOWN OR DISCOVERABLE. WHERE DISCLAIMERS OF WARRANTIES ARE NOT ALLOWED IN FULL OR IN PART, THIS DISCLAIMER MAY NOT APPLY TO YOU.

b. TO THE EXTENT POSSIBLE, IN NO EVENT WILL THE LICENSOR BE LIABLE TO YOU ON ANY LEGAL THEORY (INCLUDING, WITHOUT LIMITATION, NEGLIGENCE) OR OTHERWISE FOR ANY DIRECT, SPECIAL, INDIRECT, INCIDENTAL, CONSEQUENTIAL, PUNITIVE, EXEMPLARY, OR OTHER LOSSES, COSTS, EXPENSES, OR DAMAGES ARISING OUT OF THIS PUBLIC LICENSE OR USE OF THE LICENSED MATERIAL, EVEN IF THE LICENSOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH LOSSES, COSTS, EXPENSES, OR DAMAGES. WHERE A LIMITATION OF LIABILITY IS NOT ALLOWED IN FULL OR IN PART, THIS LIMITATION MAY NOT APPLY TO YOU.

c. The disclaimer of warranties and limitation of liability provided above shall be interpreted in a manner that, to the extent possible, most closely approximates an absolute disclaimer and waiver of all liability.

Section 6 -- Term and Termination.

a. This Public License applies for the term of the Copyright and Similar Rights licensed here. However, if You fail to comply with this Public License, then Your rights under this Public License terminate automatically.

b. Where Your right to use the Licensed Material has terminated under Section 6(a), it reinstates:

   1. automatically as of the date the violation is cured, provided
      it is cured within 30 days of Your discovery of the
      violation; or

   2. upon express reinstatement by the Licensor.

 For the avoidance of doubt, this Section 6(b) does not affect any
 right the Licensor may have to seek remedies for Your violations
 of this Public License.
c. For the avoidance of doubt, the Licensor may also offer the Licensed Material under separate terms or conditions or stop distributing the Licensed Material at any time; however, doing so will not terminate this Public License.

d. Sections 1, 5, 6, 7, and 8 survive termination of this Public License.

Section 7 -- Other Terms and Conditions.

a. The Licensor shall not be bound by any additional or different terms or conditions communicated by You unless expressly agreed.

b. Any arrangements, understandings, or agreements regarding the Licensed Material not stated herein are separate from and independent of the terms and conditions of this Public License.

Section 8 -- Interpretation.

a. For the avoidance of doubt, this Public License does not, and shall not be interpreted to, reduce, limit, restrict, or impose conditions on any use of the Licensed Material that could lawfully be made without permission under this Public License.

b. To the extent possible, if any provision of this Public License is deemed unenforceable, it shall be automatically reformed to the minimum extent necessary to make it enforceable. If the provision cannot be reformed, it shall be severed from this Public License without affecting the enforceability of the remaining terms and conditions.

c. No term or condition of this Public License will be waived and no failure to comply consented to unless expressly agreed to by the Licensor.

d. Nothing in this Public License constitutes or may be interpreted as a limitation upon, or waiver of, any privileges and immunities that apply to the Licensor or You, including from the legal processes of any jurisdiction or authority.

=======================================================================

Creative Commons is not a party to its public licenses. Notwithstanding, Creative Commons may elect to apply one of its public licenses to material it publishes and in those instances will be considered the “Licensor.” The text of the Creative Commons public licenses is dedicated to the public domain under the CC0 Public Domain Dedication. Except for the limited purpose of indicating that material is shared under a Creative Commons public license or as otherwise permitted by the Creative Commons policies published at creativecommons.org/policies, Creative Commons does not authorize the use of the trademark "Creative Commons" or any other trademark or logo of Creative Commons without its prior written consent including, without limitation, in connection with any unauthorized modifications to any of its public licenses or any other arrangements, understandings, or agreements concerning use of licensed material. For the avoidance of doubt, this paragraph does not form part of the public licenses.

Creative Commons may be contacted at creativecommons.org.
