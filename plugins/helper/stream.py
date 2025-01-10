from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from info import URL, LOG_CHANNEL
from urllib.parse import quote_plus
from Jisshu.util.file_properties import get_name, get_hash, get_media_file_size
from Jisshu.util.human_readable import humanbytes
import humanize
import random
import os

@Client.on_message(filters.private & filters.command("streams"))
async def stream_start(client, message):
    # Ask user to send the file/media
    msg = await client.ask(message.chat.id, "**Now send me your file/video to get stream and download link**")
    
    # Check if the user has replied with media
    if not msg.media:
        return await message.reply("**Please send me supported media (video or document).**")

    # Check if the media is either a VIDEO or DOCUMENT type
    if msg.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.DOCUMENT]:
        return await message.reply("**Please send a valid video or document file.**")
    
    # If the media is a valid type, retrieve file details
    file = getattr(msg, msg.media.value)
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)  # Convert size to a human-readable format
    fileid = file.file_id
    user_id = message.from_user.id
    username = message.from_user.mention

    # Display message while the file is being processed
    processing_msg = await message.reply_text("**Processing... Please wait.**")
    
    try:
        # Log the file in the log channel
        log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=fileid)
        
        # Generate stream and download links using the file's log message id and hash
        fileName = {quote_plus(get_name(log_msg))}
        stream = f"{URL}watch/{str(log_msg.id)}?hash={get_hash(log_msg)}"
        download = f"{URL}{str(log_msg.id)}?hash={get_hash(log_msg)}"
        
        # Reply with the download and stream buttons
        rm = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Stream 🖥️", url=stream),
                    InlineKeyboardButton('Download 📥', url=download)
                ]
            ]
        )
        
        msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n<b>📥 Dᴏᴡɴʟᴏᴀᴅ :</b> <i>{}</i>\n\n<b> 🖥ᴡᴀᴛᴄʜ  :</b> <i>{}</i>\n\n<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ ᴛɪʟʟ ɪ ᴅᴇʟᴇᴛᴇ</b>"""
        
        await processing_msg.edit_text(text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(msg)), download, stream), quote=True, disable_web_page_preview=True, reply_markup=rm)

    except Exception as e:
        # In case of an error, notify the user
        await processing_msg.edit_text(f"Error: {str(e)}. Please try again later.")
