# test_integration.py
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from youtube_bot import YouTubeBot

class TestIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bot = YouTubeBot("YOUR_YOUTUBE_API_KEY", "YOUR_YOUTUBE_ACCESS_TOKEN", "YOUR_YOUTUBE_LIVE_CHAT_ID")

    @patch("youtube_bot.YouTubeBot.send_message")
    @patch("youtube_bot.YouTubeBot.fetch_metar")
    async def test_handle_message_metar(self, mock_fetch_metar, mock_send_message):
        # Setup mock return value
        mock_fetch_metar.return_value = "METAR data for KJFK"

        # Simulate a user message
        message = "!metar KJFK"

        # Call the handle_message method
        await self.bot.handle_message(message)

        # Assert the expected behavior
        mock_fetch_metar.assert_called_once_with("KJFK")
        mock_send_message.assert_called_once_with("METAR data for KJFK")

    @patch("youtube_bot.YouTubeBot.send_message")
    @patch("youtube_bot.YouTubeBot.fetch_taf")
    async def test_handle_message_taf(self, mock_fetch_taf, mock_send_message):
        # Setup mock return value
        mock_fetch_taf.return_value = "TAF data for KJFK"

        # Simulate a user message
        message = "!taf KJFK"

        # Call the handle_message method
        await self.bot.handle_message(message)

        # Assert the expected behavior
        mock_fetch_taf.assert_called_once_with("KJFK")
        mock_send_message.assert_called_once_with("TAF data for KJFK")

    @patch("youtube_bot.YouTubeBot.send_message")
    @patch("youtube_bot.YouTubeBot.search_videos")
    async def test_handle_message_search(self, mock_search_videos, mock_send_message):
        # Setup mock return value
        mock_search_videos.return_value = [
            {"title": "Test Video 1", "description": "Description 1", "url": "http://youtube.com/video1"},
            {"title": "Test Video 2", "description": "Description 2", "url": "http://youtube.com/video2"},
            {"title": "Test Video 3", "description": "Description 3", "url": "http://youtube.com/video3"},
        ]

        # Simulate a user message
        message = "!search test"

        # Call the handle_message method
        await self.bot.handle_message(message)

        # Assert the expected behavior
        mock_search_videos.assert_called_once_with("test")
        expected_response = (
            "Here are the top YouTube video results:\n\n"
            "Title: Test Video 1\nDescription: Description 1\nURL: http://youtube.com/video1\n\n"
            "Title: Test Video 2\nDescription: Description 2\nURL: http://youtube.com/video2\n\n"
            "Title: Test Video 3\nDescription: Description 3\nURL: http://youtube.com/video3\n\n"
        )
        mock_send_message.assert_called_once_with(expected_response)

    # Add more test methods for other commands and scenarios

if __name__ == "__main__":
    unittest.main()
