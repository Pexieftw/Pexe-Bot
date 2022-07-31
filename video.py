import youtube_dl as ytdl
import discord
from utils import *

YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist"
}

class VideoList:
    def __init__(self, url_or_search, requested_by):
        self.videos = self._get_info(url_or_search, requested_by)
        self.is_playlist = True if len(self.videos) > 1 else False
        self.requested_by = requested_by
        self.duration = sum([video.duration for video in self.videos])
        self.likes = sum([video.likes for video in self.videos])
        self.views = sum([video.views for video in self.videos])
        self.url = url_or_search

    def _get_info(self, video_url,requested_by):
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            vidlist = []
            if "_type" in info and info["_type"] == "playlist":
                for entry in info["entries"]:
                    info = ydl.extract_info(entry["url"], download=False)
                    vid = Video(info, requested_by)
                    vidlist.append(vid)

            else:
                vid = Video(info, requested_by)
                vidlist.append(vid)
            return vidlist

    def get_embed(self):
        #Makes an embed out of this Video's information.
        embed = discord.Embed(
            title = f"New Playlist of {len(self.videos)} videos has been added",
            description = "",
            url = self.url,
            color = 0xFF0000
        )
        embed.set_footer(
            text = f"Requested by {self.requested_by.name}",
            icon_url = self.requested_by.avatar.url
        )
        if self.videos[0].thumbnail:
            embed.set_image(url=self.videos[0].thumbnail)
        if self.views:
            views = "{:,}".format(self.views)
            embed.add_field(name=f"**Total Views:**", value=f"`{views}`", inline=True)
        if self.duration:
            embed.add_field(name=f"**Total Duration:**", value=f"`{convert(self.duration)}`", inline=True)
        if self.likes:
            likes = "{:,}".format(self.likes)
            embed.add_field(name=f"**Total Likes:**", value=f"`{likes}`", inline=True)
        return embed

class Video:
    """Class containing information about a particular video."""

    def __init__(self, info, requested_by):
        """Plays audio from (or searches for) a URL."""
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:

            video = info
            video_format = video["formats"][0]
            self.stream_url = video_format["url"]
            self.video_url = video["webpage_url"]
            self.title = video["title"]
            self.uploader = video["uploader"] if "uploader" in video else ""
            self.thumbnail = video["thumbnail"] if "thumbnail" in video else None
            self.duration = video["duration"] if "duration" in video else None
            self.views = video["view_count"] if "view_count" in video else None
            self.likes = video["like_count"] if "like_count" in video else None
            self.requested_by = requested_by

    def get_embed(self):
        #Makes an embed out of this Video's information.
        embed = discord.Embed(
            title = self.title,
            description = f"**By**: {self.uploader}",
            url = self.video_url,
            color = 0xFF0000
        )
        embed.set_footer(
            text = f"Requested by {self.requested_by.name}",
            icon_url = self.requested_by.avatar.url
        )
        if self.thumbnail:
            embed.set_image(url=self.thumbnail)
        if self.views:
            views = "{:,}".format(self.views)
            embed.add_field(name=f"**Views:**", value=f"`{views}`", inline=True)
        if self.duration:
            embed.add_field(name=f"**Duration:**", value=f"`{convert(self.duration)}`", inline=True)
        if self.likes:
            likes = "{:,}".format(self.likes)
            embed.add_field(name=f"**Likes:**", value=f"`{likes}`", inline=True)
        return embed