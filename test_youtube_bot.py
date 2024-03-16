# test_youtube_bot.py
import unittest
from unittest.mock import AsyncMock, patch
from youtube_bot import YouTubeBot

class TestYouTubeBot(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bot = YouTubeBot("YOUR_YOUTUBE_API_KEY", "YOUR_YOUTUBE_ACCESS_TOKEN", "YOUR_YOUTUBE_LIVE_CHAT_ID")

    @patch("youtube_bot.make_api_request")
    async def test_search_videos(self, mock_make_api_request):
        # Mock the API response
        mock_response = {
            "items": [
                {
                    "id": {"videoId": "video_id_1"},
                    "snippet": {
                        "title": "Video 1",
                        "description": "Description 1"
                    }
                },
                {
                    "id": {"videoId": "video_id_2"},
                    "snippet": {
                        "title": "Video 2",
                        "description": "Description 2"
                    }
                }
            ]
        }
        mock_make_api_request.return_value = mock_response

        # Call the search_videos method
        videos = await self.bot.search_videos("query")

        # Assert the expected behavior
        self.assertEqual(len(videos), len(mock_response["items"]))
        self.assertEqual(videos[0]["title"], "Video 1")
        self.assertEqual(videos[0]["description"], "Description 1")
        self.assertEqual(videos[0]["url"], "https://www.youtube.com/watch?v=video_id_1")
        self.assertEqual(videos[1]["title"], "Video 2")
        self.assertEqual(videos[1]["description"], "Description 2")
        self.assertEqual(videos[1]["url"], "https://www.youtube.com/watch?v=video_id_2")

    @patch("youtube_bot.make_api_request")
    async def test_get_video_info(self, mock_make_api_request):
        # Mock the API response
        mock_response = {
            "items": [
                {
                    "snippet": {
                        "title": "Video Title",
                        "description": "Video Description"
                    },
                    "statistics": {
                        "viewCount": "1000",
                        "likeCount": "50",
                        "commentCount": "10"
                    }
                }
            ]
        }
        mock_make_api_request.return_value = mock_response

        # Call the get_video_info method
        video_info = await self.bot.get_video_info("video_id")

        # Assert the expected behavior
        self.assertEqual(video_info["title"], "Video Title")
        self.assertEqual(video_info["description"], "Video Description")
        self.assertEqual(video_info["views"], "1000")
        self.assertEqual(video_info["likes"], "50")
        self.assertEqual(video_info["comments"], "10")

    # Add more test methods for other functions like fetch_metar, fetch_taf, etc.

if __name__ == "__main__":
    unittest.main()