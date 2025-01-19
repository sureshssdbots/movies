from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import CHANNELS, MOVIE_UPDATE_CHANNEL, ADMINS, LOG_CHANNEL
from database.ia_filterdb import save_file, unpack_new_file_id, delete_duplicate_file
from utils import get_poster, temp
import re
from Script import script
from database.users_chats_db import db

processed_movies = set()
media_filter = filters.document | filters.video

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    try:
        media = getattr(message, message.media.value, None)
        if not media or media.mime_type not in ['video/mp4', 'video/x-matroska']:
            return  # Unsupported file type

        media.file_type = message.media.value
        media.caption = message.caption

        # Check for duplicate and delete if found
        file_name = name_format(media.file_name)
        duplicate_deleted = await delete_duplicate_file(file_name)

        if duplicate_deleted:
            await bot.send_message(LOG_CHANNEL, f"Duplicate file removed: {file_name}")

        # Save new file
        success_sts = await save_file(media)
        if success_sts == 'suc':
            file_id, file_ref = unpack_new_file_id(media.file_id)
            await send_movie_updates(bot, file_name=media.file_name, file_id=file_id)
    except Exception as e:
        await bot.send_message(LOG_CHANNEL, f"Error in processing media: <code>{e}</code>")

def name_format(file_name: str) -> str:
    file_name = re.sub(r'http\S+', '', re.sub(r'@\w+|#\w+', '', file_name.replace('_', ' ').replace('[', '').replace(']', ''))).strip()
    file_name = re.split(r's\d+|season\s*\d+|chapter\s*\d+', file_name, flags=re.IGNORECASE)[0]
    return file_name.strip()

async def get_imdb(file_name: str):
    try:
        imdb_file_name = name_format(file_name)
        imdb = await get_poster(imdb_file_name)
        if imdb:
            caption = script.MOVIES_UPDATE_TXT.format(
                title=imdb.get('title'),
                rating=imdb.get('rating'),
                genres=imdb.get('genres'),
                year=imdb.get('year')
            )
            return imdb.get('title'), imdb.get('poster'), caption
    except Exception as e:
        print(f"Error fetching IMDB data: {e}")
    return None, None, None

async def send_movie_updates(bot, file_name: str, file_id: str):
    try:
        imdb_title, poster_url, caption = await get_imdb(file_name)
        if not imdb_title or imdb_title in processed_movies:
            return  # Already processed or IMDB data not found

        processed_movies.add(imdb_title)
        if not poster_url or not caption:
            await bot.send_message(LOG_CHANNEL, f"Poster or caption missing for file: {file_name}")
            return
btn = [
    [InlineKeyboardButton('🎥 Get File', url=f'https://t.me/{temp.U_NAME}?start={file_name}')]
]
reply_markup = InlineKeyboardMarkup(btn)
        

        movie_update_channel = await db.movies_update_channel_id()
        target_channel = movie_update_channel if movie_update_channel else MOVIE_UPDATE_CHANNEL

        await bot.send_photo(
            target_channel,
            photo=poster_url,
            caption=caption,
            reply_markup=reply_markup
        )
    except Exception as e:
        error_msg = f"Failed to send movie update. Error: <code>{e}</code>"
        print(error_msg)
        await bot.send_message(LOG_CHANNEL, error_msg)
