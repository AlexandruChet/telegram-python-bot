import os
from dotenv import load_dotenv
from aiogram import Dispatcher, Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from os import getenv
import asyncio
import yt_dlp
from typing import Callable

import sys
sys.dont_write_bytecode = True
sys.path.append("./bot_func")

from v_download import download_video_sync # type: ignore

load_dotenv()
TOKEN = getenv("TOKEN")
bot = Bot(token=TOKEN)  # type: ignore
dp = Dispatcher()
router = Router()

dp.include_router(router)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Hi")



async def _video_download(message: Message, url: str, path: str, download_func: Callable):
    await message.answer("Downloading...")

    try:
        os.makedirs(f"{path}", exist_ok=True)
        filename = await asyncio.to_thread(download_func, url)

        if not os.path.exists(filename):
            print("Error, file not found")

        video = FSInputFile(filename)
        await message.answer_video(video)
        os.remove(filename)

    except Exception as err:
        print(f"Downloading error {err}")
        await message.answer("ERROR Try again")


@dp.message(Command("download_video"))
async def video_download(message: Message):
    text = message.text.split()  # type: ignore

    if len(text) < 2:
        await message.answer("Usage:\n" "/video URL")
        return

    url = text[1]
    await _video_download(message, url, "video_downloads", download_video_sync)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
