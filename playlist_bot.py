import logging
import os
import sys

from clientlibs import PlaylistBotClient


class PlaylistBot:
    def __init__(self): 
        logging.basicConfig(
            datefmt="%Y/%m/%d %H:%M:%S",
            filename="playlist_bot.log",
            format="%(asctime)s %(name)s:%(levelname)s %(message)s",
            level=logging.INFO,
        )
        self.logger = logging.getLogger("playlist_bot")
        self.TOKEN = os.getenv("DISCORD_TOKEN")
        self.discord_client = self.get_discord_client()

    def get_discord_client(self):
        return PlaylistBotClient(logger=self.logger)

    def run(self):
        self.discord_client.run(self.TOKEN)

    def get_discord_client_loop(self):
        return self.discord_client.loop


if __name__ == "__main__":
    pb = PlaylistBot()
    pb.run()
