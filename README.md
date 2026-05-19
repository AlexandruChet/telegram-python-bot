# Telegram File Bot

A Python Telegram bot for downloading videos and audio from various platforms (YouTube, TikTok, etc.) using the `yt-dlp` library.

## Development Note
To prevent the generation of `__pycache__` cache files, the project uses:
```python
import sys
sys.dont_write_bytecode = True
```