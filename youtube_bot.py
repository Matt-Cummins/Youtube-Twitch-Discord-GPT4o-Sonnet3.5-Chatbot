```python
# youtube_bot.py
import os
import logging
import asyncio
import requests
from config import Config
from utils import make_api_request, get_continuous_chunks, perform_web_search, format_search_results
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

class YouTubeBot:
    """
    A YouTube bot that interacts with the YouTube API to perform various tasks.
    """

    def __init__(self, api_key, access_token, live_chat_id):
        """
        Initialize the YouTubeBot instance.

        Args:
            api_key (str): The YouTube API key.
            access_token (str): The YouTube access token.
            live_chat_id (str): The ID of the YouTube live chat.
        """
        self.api_key = api_key
        self.access_token = access_token
        self.live_chat_id = live_chat_id

    async def search_videos(self, query):
        """
        Search for YouTube videos based on the provided query.

        Args:
            query (str): The search query.

        Returns:
            list: A list of dictionaries containing video information, or None if an error occurred.
        """
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "key": self.api_key,
            "maxResults": 3
        }
        try:
            data = await make_api_request(url, params)
            if data:
                videos = [
                    {
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                    }
                    for item in data["items"]
                ]
                return videos
            else:
                return None
        except Exception as e:
            logging.error(f"Error searching YouTube videos: {e}")
            return None

    async def get_video_info(self, video_id):
        """
        Retrieve information about a specific YouTube video.

        Args:
            video_id (str): The ID of the YouTube video.

        Returns:
            dict: A dictionary containing video information, or None if an error occurred.
        """
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet,statistics",
            "id": video_id,
            "key": self.api_key
        }
        try:
            data = await make_api_request(url, params)
            if data and "items" in data and len(data["items"]) > 0:
                video = data["items"][0]
                return {
                    "title": video["snippet"]["title"],
                    "description": video["snippet"]["description"],
                    "views": video["statistics"]["viewCount"],
                    "likes": video["statistics"]["likeCount"],
                    "comments": video["statistics"]["commentCount"]
                }
            else:
                return None
        except Exception as e:
            logging.error(f"Error retrieving video information: {e}")
            return None

    async def get_channel_info(self, channel_id):
        """
        Retrieve information about a specific YouTube channel.

        Args:
            channel_id (str): The ID of the YouTube channel.

        Returns:
            dict: A dictionary containing channel information, or None if an error occurred.
        """
        url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "part": "snippet,statistics",
            "id": channel_id,
            "key": self.api_key
        }
        try:
            data = await make_api_request(url, params)
            if data and "items" in data and len(data["items"]) > 0:
                channel = data["items"][0]
                return {
                    "name": channel["snippet"]["title"],
                    "description": channel["snippet"]["description"],
                    "subscribers": channel["statistics"]["subscriberCount"],
                    "views": channel["statistics"]["viewCount"],
                    "videos": channel["statistics"]["videoCount"]
                }
            else:
                return None
        except Exception as e:
            logging.error(f"Error retrieving channel information: {e}")
            return None

    async def fetch_metar(self, station_code):
        """
        Fetch METAR data for a given station code.

        Args:
            station_code (str): The ICAO station code.

        Returns:
            str: The METAR data and translation, or an error message if an error occurred.
        """
        url = f"https://avwx.rest/api/metar/{station_code}?options=info,translate"
        headers = {"Authorization": f"BEARER {Config.AVWX_API_KEY}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            metar = data['raw']
            translation = data['translate']['summary']
            return f"METAR for {station_code}:\n{metar}\n\nTranslation: {translation}"
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching METAR data: {e}")
            return "Failed to fetch METAR data. Please try again later."

    async def fetch_taf(self, station_code):
        """
        Fetch TAF data for a given station code.

        Args:
            station_code (str): The ICAO station code.

        Returns:
            str: The TAF data and translation, or an error message if an error occurred.
        """
        url = f"https://avwx.rest/api/taf/{station_code}?options=translate"
        headers = {"Authorization": f"BEARER {Config.AVWX_API_KEY}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            taf = data['raw']
            translation = data['translate']['summary']
            return f"TAF for {station_code}:\n{taf}\n\nTranslation: {translation}"
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching TAF data: {e}")
            return "Failed to fetch TAF data. Please try again later."

    async def fetch_notam(self, station_code):
        """
        Fetch NOTAM data for a given station code.

        Args:
            station_code (str): The ICAO station code.

        Returns:
            str: The NOTAM data, or an error message if an error occurred.
        """
        url = f"https://applications.icao.int/dataservices/api/notams-realtime-list?api_key={Config.ICAO_API_KEY}&format=json&criticality=1&locations={station_code}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            notams = data['notams']
            if notams:
                notam_text = "\n".join(notam['all'] for notam in notams)
                return f"NOTAMs for {station_code}:\n{notam_text}"
            else:
                return f"No NOTAMs found for {station_code}."
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching NOTAM data: {e}")
            return "Failed to fetch NOTAM data. Please try again later."

    async def fetch_aircraft_info(self, aircraft_type):
        """
        Fetch information about a specific aircraft type.

        Args:
            aircraft_type (str): The aircraft type (ICAO code).

        Returns:
            str: The aircraft information, or an error message if an error occurred.
        """
        url = f"https://aerodatabox.p.rapidapi.com/aircrafts/icao/{aircraft_type}"
        headers = {
            "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com",
            "X-RapidAPI-Key": Config.RAPIDAPI_KEY
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            manufacturer = data['manufacturer']
            model = data['model']
            return f"Aircraft Information for {aircraft_type}:\nManufacturer: {manufacturer}\nModel: {model}"
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching aircraft information: {e}")
            return "Failed to fetch aircraft information. Please try again later."

    async def fetch_airport_info(self, airport_code):
        """
        Fetch information about a specific airport.

        Args:
            airport_code (str): The IATA airport code.

        Returns:
            str: The airport information, or an error message if an error occurred.
        """
        url = f"https://aerodatabox.p.rapidapi.com/airports/iata/{airport_code}"
        headers = {
            "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com",
            "X-RapidAPI-Key": Config.RAPIDAPI_KEY
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            name = data['name']
            location = f"{data['location']['city']}, {data['location']['country']}"
            return f"Airport Information for {airport_code}:\nName: {name}\nLocation: {location}"
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching airport information: {e}")
            return "Failed to fetch airport information. Please try again later."

    async def fetch_chart_info(self, chart_name):
        """
        Fetch information about a specific chart.

        Args:
            chart_name (str): The name of the chart.

        Returns:
            str: The chart information, or an error message if an error occurred.
        """
        url = f"https://api.navigraph.com/v1/charts/{chart_name}"
        headers = {
            "Authorization": f"Bearer {Config.NAVIGRAPH_API_KEY}",
            "Accept": "application/json"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            chart_info = f"Chart Information for {chart_name}:\n"
            chart_info += f"Name: {data['name']}\n"
            chart_info += f"ICAO Code: {data['icaoCode']}\n"
            chart_info += f"Chart Type: {data['chartType']}\n"
            chart_info += f"Published Date: {data['publicationDate']}\n"
            return chart_info
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching chart information: {e}")
            return "Failed to fetch chart information. Please try again later."

    async def fetch_weather_info(self, location):
        """
        Fetch weather information for a specific location.

        Args:
            location (str): The location (city name).

        Returns:
            str: The weather information, or an error message if an error occurred.
        """
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={Config.OPENWEATHERMAP_API_KEY}&units=metric"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            description = data['weather'][0]['description']
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            return f"Weather Information for {location}:\nDescription: {description}\nTemperature: {temperature}°C\nHumidity: {humidity}%\nWind Speed: {wind_speed} m/s"
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching weather information: {e}")
            return "Failed to fetch weather information. Please try again later."

    async def send_message(self, message):
        """
        Send a message to the YouTube live chat.

        Args:
            message (str): The message to send.
        """
        url = "https://www.googleapis.com/youtube/v3/liveChat/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "snippet": {
                "type": "textMessageEvent",
                "liveChatId": self.live_chat_id,
                "textMessageDetails": {
                    "messageText": message
                }
            }
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            logging.info(f"Message sent to YouTube chat: {message}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending message to YouTube chat: {e}")

    async def handle_message(self, message):
        """
        Handle incoming messages from the YouTube live chat.

        Args:
            message (str): The message received from the live chat.
        """
        if message.startswith("!search"):
            query = message.replace("!search", "").strip()
            videos = await self.search_videos(query)
            if videos:
                response = "Here are the top YouTube video results:\n\n"
                for video in videos:
                    response += f"Title: {video['title']}\n"
                    response += f"Description: {video['description']}\n"
                    response += f"URL: {video['url']}\n\n"
            else:
                response = "No YouTube videos found for the given query."
            await self.send_message(response)
        elif message.startswith("!videoinfo"):
            video_id = message.replace("!videoinfo", "").strip()
            video_info = await self.get_video_info(video_id)
            if video_info:
                response = f"Video Information:\n\n"
                response += f"Title: {video_info['title']}\n"
                response += f"Description: {video_info['description']}\n"
                response += f"Views: {video_info['views']}\n"
                response += f"Likes: {video_info['likes']}\n"
                response += f"Comments: {video_info['comments']}\n"
            else:
                response = "No video information found for the given video ID."
            await self.send_message(response)
        elif message.startswith("!channelinfo"):
            channel_id = message.replace("!channelinfo", "").strip()
            channel_info = await self.get_channel_info(channel_id)
            if channel_info:
                response = f"Channel Information:\n\n"
                response += f"Name: {channel_info['name']}\n"
                response += f"Description: {channel_info['description']}\n"
                response += f"Subscribers: {channel_info['subscribers']}\n"
                response += f"Views: {channel_info['views']}\n"
                response += f"Videos: {channel_info['videos']}\n"
            else:
                response = "No channel information found for the given channel ID."
            await self.send_message(response)
        elif message.startswith("!metar"):
            station_code = message.replace("!metar", "").strip().upper()
            if len(station_code) == 4:
                metar_data = await self.fetch_metar(station_code)
                await self.send_message(metar_data)
            else:
                await self.send_message("Please provide a valid 4-letter ICAO station code.")
        elif message.startswith("!taf"):
            station_code = message.replace("!taf", "").strip().upper()
            if len(station_code) == 4:
                taf_data = await self.fetch_taf(station_code)
                await self.send_message(taf_data)
            else:
                await self.send_message("Please provide a valid 4-letter ICAO station code.")
        elif message.startswith("!notam"):
            station_code = message.replace("!notam", "").strip().upper()
            if len(station_code) == 4:
                notam_data = await self.fetch_notam(station_code)
                await self.send_message(notam_data)
            else:
                await self.send_message("Please provide a valid 4-letter ICAO station code.")
        elif message.startswith("!aircraft"):
            aircraft_type = message.replace("!aircraft", "").strip()
            aircraft_info = await self.fetch_aircraft_info(aircraft_type)
            await self.send_message(aircraft_info)
        elif message.startswith("!airport"):
            airport_code = message.replace("!airport", "").strip().upper()
            if len(airport_code) == 3:
                airport_info = await self.fetch_airport_info(airport_code)
                await self.send_message(airport_info)
            else:
                await self.send_message("Please provide a valid 3-letter IATA airport code.")
        elif message.startswith("!chart"):
            chart_name = message.replace("!chart", "").strip()
            chart_info = await self.fetch_chart_info(chart_name)
            await self.send_message(chart_info)
        elif message.startswith("!weather"):
            location = message.replace("!weather", "").strip()
            weather_info = await self.fetch_weather_info(location)
            await self.send_message(weather_info)
        else:
            # Handle other common messages or default response
            response = "I'm sorry, I don't understand your request. Please try one of the following commands:\n\n"
            response += "!search <query> - Search for YouTube videos\n"
            response += "!videoinfo <video_id> - Get information about a specific video\n"
            response += "!channelinfo <channel_id> - Get information about a specific channel\n"
            response += "!metar <station_code> - Get METAR data for a given station\n"
            response += "!taf <station_code> - Get TAF data for a given station\n"
            response += "!notam <station_code> - Get NOTAM data for a given station\n"
            response += "!aircraft <aircraft_type> - Get information about a specific aircraft type\n"
            response += "!airport <airport_code> - Get information about a specific airport\n"
            response += "!chart <chart_name> - Get information about a specific chart\n"
            response += "!weather <location> - Get weather information for a specific location\n"
            await self.send_message(response)

async def retrieve_youtube_chat_messages():
    """
    Retrieve messages from the YouTube live chat.

    Returns:
        list: A list of dictionaries containing the author and message of each chat message.
    """
    try:
        # Set up the YouTube API client
        youtube = build('youtube', 'v3', credentials=get_youtube_credentials())

        # Make a request to retrieve the chat messages
        chat_messages = []
        next_page_token = None

        while True:
            request = youtube.liveChatMessages().list(
                liveChatId=Config.YOUTUBE_LIVE_CHAT_ID,
                part='snippet,authorDetails',
                pageToken=next_page_token
            )
            response = request.execute()

            # Extract the relevant message data from the API response
            for message in response['items']:
                chat_messages.append({
                    'author': message['authorDetails']['displayName'],
                    'message': message['snippet']['displayMessage']
                })

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break

        return chat_messages

    except Exception as e:
        logging.error(f"Error retrieving YouTube chat messages: {e}")
        return []

def get_youtube_credentials():
    """
    Get the YouTube API credentials.

    Returns:
        google.oauth2.credentials.Credentials: The YouTube API credentials.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/youtube.force-ssl'])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', ['https://www.googleapis.com/auth/youtube.force-ssl'])
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

async def run_youtube_bot():
    """
    Run the YouTube bot.
    """
    youtube_bot = YouTubeBot(Config.YOUTUBE_API_KEY, Config.YOUTUBE_ACCESS_TOKEN, Config.YOUTUBE_LIVE_CHAT_ID)
    while True:
        try:
            # Retrieve messages from YouTube chat
            messages = await retrieve_youtube_chat_messages()
            for message in messages:
                await youtube_bot.handle_message(message['message'])
        except Exception as e:
            logging.error(f"Error in YouTube bot: {e}")
        await asyncio.sleep(5)  # Wait for 5 seconds before retrieving messages again