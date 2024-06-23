import os

class Config:
    """
    A class to manage configuration variables loaded from environment variables.
    """

    @staticmethod
    def get_env_variable(name, default=None, required=False):
        """
        Retrieve the value of an environment variable.

        Args:
            name (str): The name of the environment variable.
            default (Any): The default value to return if the environment variable is not set.
            required (bool): Indicates whether the environment variable is required.

        Returns:
            The value of the environment variable, or the default value if not set.

        Raises:
            ValueError: If the environment variable is required but not set.
        """
        value = os.getenv(name, default)
        if required and value is None:
            raise ValueError(f"Environment variable {name} is required but not set.")
        return value

    @classmethod
    def load_configuration(cls):
        """
        Load configuration values from environment variables and assign them to class variables.
        """
        cls.DISCORD_BOT_TOKEN = cls.get_env_variable('DISCORD_BOT_TOKEN', required=True)
        cls.TWITCH_CLIENT_ID = cls.get_env_variable('TWITCH_CLIENT_ID', required=True)
        cls.TWITCH_CLIENT_SECRET = cls.get_env_variable('TWITCH_CLIENT_SECRET', required=True)
        cls.OPENAI_API_KEY = cls.get_env_variable('OPENAI_API_KEY', required=True)
        cls.GOOGLE_PSE_ID = cls.get_env_variable('GOOGLE_PSE_ID', required=True)
        cls.GOOGLE_PSE_API_KEY = cls.get_env_variable('GOOGLE_PSE_API_KEY', required=True)
        cls.TWITCH_BOT_NAME = cls.get_env_variable('TWITCH_BOT_NAME', 'defaultBotName')
        cls.TWITCH_BOT_TOKEN = cls.get_env_variable('TWITCH_BOT_TOKEN', required=True)
        cls.TWITCH_CHANNEL_NAME = cls.get_env_variable('TWITCH_CHANNEL_NAME', 'defaultChannelName')
        cls.YOUTUBE_API_KEY = cls.get_env_variable('YOUTUBE_API_KEY', required=True)
        cls.YOUTUBE_ACCESS_TOKEN = cls.get_env_variable('YOUTUBE_ACCESS_TOKEN', required=True)
        cls.YOUTUBE_LIVE_CHAT_ID = cls.get_env_variable('YOUTUBE_LIVE_CHAT_ID', required=True)
        cls.AVWX_API_KEY = cls.get_env_variable('AVWX_API_KEY', required=True)
        cls.ICAO_API_KEY = cls.get_env_variable('ICAO_API_KEY', required=True)
        cls.RAPIDAPI_KEY = cls.get_env_variable('RAPIDAPI_KEY', required=True)
        cls.OPENWEATHERMAP_API_KEY = cls.get_env_variable('OPENWEATHERMAP_API_KEY', required=True)
        cls.AVIATION_EDGE_API_KEY = cls.get_env_variable('AVIATION_EDGE_API_KEY', required=True)
        cls.NAVIGRAPH_API_KEY = cls.get_env_variable('NAVIGRAPH_API_KEY', required=True)
        cls.ACCESS_TOKEN = None
        cls.TOKEN_EXPIRY = 0

# Example usage
if __name__ == "__main__":
    Config.load_configuration()
    print(f"Discord Bot Token: {Config.DISCORD_BOT_TOKEN}")
