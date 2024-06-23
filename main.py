# main.py
import asyncio
from config import Config
from discord_bot import run_discord_bot
from twitch_bot import run_twitch_bot
from youtube_bot import YouTubeBot, run_youtube_bot

async def main():
    """
    The main function that runs the bots concurrently.
    """
    try:
        # Load the configuration
        Config.load_configuration()

        # Create tasks for running each bot
        discord_task = asyncio.create_task(run_discord_bot())
        twitch_task = asyncio.create_task(run_twitch_bot())

        # Create an instance of the YouTubeBot
        youtube_bot = YouTubeBot(Config.YOUTUBE_API_KEY, Config.YOUTUBE_ACCESS_TOKEN, Config.YOUTUBE_LIVE_CHAT_ID)

        # Create a task for running the YouTube bot
        youtube_task = asyncio.create_task(run_youtube_bot(youtube_bot))

        # Run all the tasks concurrently
        await asyncio.gather(discord_task, twitch_task, youtube_task)

    except Exception as e:
        logging.error(f"An error occurred while running the bots: {e}")

if __name__ == '__main__':
    # Run the main function
    asyncio.run(main())
