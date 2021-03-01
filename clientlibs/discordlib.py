import discord
import logging
import os
import re

from typing import Optional

from .youtubelib import YoutubeClient, YoutubeException, NotAVideoException


class PlaylistBotClient(discord.Client):
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("playlist_bot")
        self.GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
        self.LISTEN_CHANNEL = os.getenv("DISCORD_LISTEN_CHANNEL")
        self.YOUTUBE_PLAYLIST_ID = os.getenv("YOUTUBE_PLAYLIST_ID")  # TODO: monthly playlists?
        self.youtube_client = YoutubeClient(self.logger)
        super(PlaylistBotClient, self).__init__()

    def get_playlist_url(self, playlist_id: Optional[str] = None) -> str:
        playlist_id = playlist_id or self.YOUTUBE_PLAYLIST_ID
        return f"https://www.youtube.com/playlist?list={playlist_id}"

    async def on_ready(self):
            self.logger.info("%s has connected to Discord!", self.user)
            guild = discord.utils.get(self.guilds, id=self.GUILD_ID)
            if not guild:
                self.logger.error(f"Bot is not a member of the right guild!")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.name == self.LISTEN_CHANNEL:
            self.logger.info("Message received: %s", message.content)
            # TODO: support multiple URLs in single message
            result = re.search(r"(?P<url>https?://[^\s]+)", message.content)
            url = result.group("url")
            if "youtube" in url or "youtu.be" in url:
                response = self.youtube_client.insert_video_url_into_playlist(
                    playlist_id=self.YOUTUBE_PLAYLIST_ID,
                    video_url=url,
                )
                self.logger.info("Response received: %s", response)
                playlist_item_id = response.get("id")
                await message.channel.send(f"Added {playlist_item_id} to {self.get_playlist_url()}")

    # async def on_error(self, event, *args, **kwargs):
    #     pass
