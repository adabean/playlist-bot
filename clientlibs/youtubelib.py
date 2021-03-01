# -*- coding: utf-8 -*-

# Sample Python code for youtube.playlistItems.insert
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

from typing import Optional

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import json
import logging
import os
import urllib


class YoutubeException(Exception):
    pass


class NotAVideoException(YoutubeException):
    pass


class YoutubeClient:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("playlist_bot")
        self.client = self.auth_and_get_client()

    def get_video_id_from_yturl(self, url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc == "www.youtube.com" and parsed.path == "/watch":
            query = urllib.parse.parse_qs(parsed.query)
            maybe_video_id = query.get("v")
            if len(maybe_video_id) == 1:  # yeah it's a list lol
                return maybe_video_id[0]
            else:
                raise NotAVideoException(f"URL {url} confused the regex, we got {maybe_video_id}")
            raise NotAVideoException(f"URL {url} does not look like a Youtube video URL")
        # test example: https://youtu.be/feP6dT89XXA?t=3
        elif parsed.netloc == "youtu.be":
            return parsed.path[1:]
        raise YoutubeException(f"URL {url} does not look like a Youtube URL")


    def auth_and_get_client(self):
        api_service_name = "youtube"
        api_version = "v3"
        client_secret_str = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET_FILE_CONTENT")
        if not client_secret_str:
            raise ValueError("Could not load Google OAuth client secret")
        client_secret = json.loads(client_secret_str)
        scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(client_secret, scopes)
        credentials = flow.run_console()
        return googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

    def insert_video_into_playlist(self, playlist_id: str, video_id: str, position: Optional[int] = None):
        request_body = {
          "snippet": {
            "playlistId": playlist_id,
            "resourceId": {
              "kind": "youtube#video",
              "videoId": video_id
            }
          }
        }
        # TODO: lopri: test adding position to message
        if isinstance(position, int):  # position=0 is valid
            request_body["snippet"]["position"] = position

        self.logger.info("Executing request body: %s", request_body)

        # pylint: disable=maybe-no-member
        request = self.client.playlistItems().insert(
            part="snippet",
            body=request_body,
        )
        response = request.execute()
        return response

    def insert_video_url_into_playlist(self, playlist_id: str, video_url: str, position: Optional[int] = None):
        return self.insert_video_into_playlist(
            playlist_id=playlist_id,
            video_id=self.get_video_id_from_yturl(url=video_url),
            position=position,
        )
