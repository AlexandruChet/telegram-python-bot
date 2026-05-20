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

from v_download import download_video_sync
from v_download import download_audio_sync
from v_download import download_video_with_subs

load_dotenv()
TOKEN = getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

dp.include_router(router)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Hi")


async def _download_dispatcher(
    message: Message,
    url: str,
    path: str,
    download_func: Callable[[str, str], str],
    file_type: str,
):
    status_msg = await message.answer("Downloading...")

    try:
        os.makedirs(path, exist_ok=True)

        filename = await asyncio.to_thread(download_func, url, path)

        if not os.path.exists(filename):
            print(f"File {filename} not found.")

        await status_msg.delete()

        input_file = FSInputFile(filename)

        if file_type == "video":
            await message.answer_video(input_file)
        elif file_type == "audio":
            await message.answer_audio(input_file)

        os.remove(filename)

    except Exception as err:
        print(f"Downloading error: {err}")
        await message.answer("ERROR. Try again later.")


@router.message(Command("download_video"))
async def video_download(message: Message):
    text = message.text.split()

    if len(text) < 2:
        await message.answer("Usage:\n/download_video URL")
        return

    url = text[1]
    await _download_dispatcher(
        message, url, "video_downloads", download_video_sync, "video"
    )


@dp.message(Command("download_audio"))
async def audio_download(message: Message):
    text = message.text.split()

    if len(text) < 2:
        await message.answer("Usage:\n" "/download_audio URL")
        return

    url = text[1]
    await _download_dispatcher(
        message, url, "audio_downloads", download_audio_sync, "audio"
    )


@dp.message(Command("add_subs"))
async def add_video_subs(message: Message):
    text = message.text.split()

    if len(text) < 2:
        await message.answer("Usage:\n/add_subs URL [language]")
        return
    
    url = text[1]
    
    language = text[2] if len(text) > 2 else "en"
    await _download_dispatcher(
        message=message, 
        url=url, 
        path="video_with_subs", 
        download_func=lambda u, p: download_video_with_subs(u, p, language),
        file_type="video"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
