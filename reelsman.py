import os
import re
import yt_dlp
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatAction
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.client.default import DefaultBotProperties

# Load token from Railway environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

VIDEO_URL_REGEX = r'(https?://[^\s]+)'
SUPPORTED_DOMAINS = ['instagram.com']

def is_supported_url(url: str) -> bool:
    return any(domain in url for domain in SUPPORTED_DOMAINS)

def get_direct_video_url(url: str) -> str or None:
    ydl_opts = {
        'format': 'best[height<=720]/best',
        'quiet': True,
        'no_warnings': True,
        'skip_download': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info.get("url")
        except Exception as e:
            logging.error(f"[ERROR] URL extraction failed: {e}")
            return None

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Updates", url="https://t.me/WorkGlows"),
            InlineKeyboardButton(text="Support", url="https://t.me/TheCryptoElders")
        ],
        [
            InlineKeyboardButton(
                text="Add Me To Your Group",
                url=f"https://t.me/{(await bot.me()).username}?startgroup=true"
            )
        ]
    ])

    text = (
        "<b>🎬 Instagram Video Downloader</b>\n\n"
        "Simply send an Instagram video link and I'll reply with a direct download link.\n\n"
        "✅ No bandwidth usage\n"
        "⚠️ Private or age-restricted videos aren't supported\n\n"
        "Enjoy lightning-fast video access!"
    )
    await message.answer(text, reply_markup=keyboard)

@dp.message()
async def handle_video_message(message: Message):
    url_match = re.search(VIDEO_URL_REGEX, message.text or "")
    if not url_match:
        return

    url = url_match.group(1)

    if not is_supported_url(url):
        return

    logging.info(f"[REQUEST] Instagram URL received: {url}")

    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    direct_url = get_direct_video_url(url)
    if direct_url:
        await message.reply(
            f"<a href=\"{direct_url}\">ㅤ</a>",
            parse_mode="HTML"
        )
        logging.info("[RESPONSE] Direct link sent successfully.")
    else:
        await message.reply("Chud Gaye Ghuru 😢")
        logging.warning("[RESPONSE] Failed to extract video link.")

async def set_commands():
    await bot.set_my_commands([
        BotCommand(command="start", description="Bot info & how to use")
    ])

async def main():
    await set_commands()
    logging.info("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
