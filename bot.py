import os
import asyncio
import sys
from os import getenv
from typing import Callable
from dotenv import load_dotenv
from aiogram import Dispatcher, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from PIL import Image

sys.dont_write_bytecode = True
sys.path.append("./bot_func")

from v_download import (
    download_video_sync,
    download_audio_sync,
    download_video_with_subs,
)

load_dotenv()
TOKEN = getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

waiting_for_photo = set()


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
            await status_msg.edit_text("file download failed")
            return

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


@dp.message(Command("download_video"))
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
        await message.answer("Usage:\n/download_audio URL")
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
        file_type="video",
    )


@dp.message(Command("photo_to_pdf"))
async def photo_to_pdf(message: Message):
    waiting_for_photo.add(message.from_user.id)

    await message.answer("Plesase add photo")


@dp.message(F.photo)
async def pdf_command(message: Message):

    user_id = message.from_user.id

    if user_id not in waiting_for_photo:
        return

    image_path = f"{user_id}.jpg"
    pdf_path = f"{user_id}.pdf"

    try:

        photo = message.photo[-1]

        file = await bot.get_file(photo.file_id)

        await bot.download_file(
            file.file_path,
            image_path
        )

        image = Image.open(image_path)

        if image.mode != "RGB":
            image = image.convert("RGB")

        image.save(pdf_path, "PDF")

        pdf_file = FSInputFile(pdf_path)

        await message.answer_document(
            pdf_file,
            caption="Finish"
        )

    except Exception as err:

        print(err)

        await message.answer(
            "PDF convert error"
        )

    finally:

        waiting_for_photo.remove(user_id)

        if os.path.exists(image_path):
            os.remove(image_path)

        if os.path.exists(pdf_path):
            os.remove(pdf_path)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
