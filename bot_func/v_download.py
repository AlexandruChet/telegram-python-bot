def download_video_sync(url: str) -> str:
    import yt_dlp
    import os
    import sys

    sys.dont_write_bytecode = True

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": "video_downloads/%(id)s.%(ext)s",
        "merge_output_format": "mp4",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl: # type: ignore
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        
        mp4_file = os.path.splitext(filename)[0] + ".mp4"

        if os.path.exists(mp4_file):
            return mp4_file
        return filename