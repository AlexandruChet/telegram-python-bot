import os
import sys
import yt_dlp

sys.dont_write_bytecode = True


def _base_download(
    url: str, path: str, ydl_opts: dict, extension: str, leng: str | None = None
) -> str:
    ydl_opts["outtmpl"] = f"{path}/%(id)s.%(ext)s"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

        target_file = os.path.splitext(filename)[0] + extension

        if os.path.exists(target_file):
            return target_file
        return filename


def download_video_sync(url: str, path: str) -> str:
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "quiet": True,
    }
    return _base_download(url, path, ydl_opts, ".mp4")


def download_audio_sync(url: str, path: str) -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    return _base_download(url, path, ydl_opts, ".mp3")


def download_video_with_subs(url: str, path: str, language: str = "en"):
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [language],
        "subtitlesformat": "srt",
        "postprocessors": [
            {
                "key": "FFmpegEmbedSubtitle",
            }
        ],
        "merge_output_format": "mp4",
        "outtmpl": "%(title)s.%(ext)s",
    }

    return _base_download(url, path, ydl_opts, ".mp4", language)
