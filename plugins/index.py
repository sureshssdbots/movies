import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from utils import temp, get_readable_time
from database.ia_filterdb import save_file

lock = asyncio.Lock()

# Command: /index (Start Indexing)
@Client.on_message(filters.command('index') & filters.private)
async def start_index(bot, message):
    if lock.locked():
        return await message.reply("⚠️ Indexing is already in progress. Please wait.")

    await message.reply("📌 Send the last message link or forward the last message from the channel to start indexing.")
    user_response = await bot.listen(message.chat.id)

    if user_response.text and user_response.text.startswith("https://t.me/"):
        try:
            link_parts = user_response.text.split("/")
            last_msg_id = int(link_parts[-1])
            chat_id = link_parts[-2]
            if chat_id.isnumeric():
                chat_id = int("-100" + chat_id)
        except:
            return await message.reply("❌ Invalid message link. Please check and try again.")
    elif user_response.forward_from_chat and user_response.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = user_response.forward_from_message_id
        chat_id = user_response.forward_from_chat.id
    else:
        return await message.reply("❌ This is not a valid forwarded message or link.")

    try:
        channel = await bot.get_chat(chat_id)
    except Exception as e:
        return await message.reply(f"❌ Error: {e}")

    if channel.type != enums.ChatType.CHANNEL:
        return await message.reply("⚠️ I can only index channels.")

    await message.reply("📌 Send the number of messages to skip (default: 0).")
    skip_response = await bot.listen(message.chat.id)
    try:
        skip_count = int(skip_response.text)
    except:
        return await message.reply("❌ Invalid number. Please enter a valid number.")

    buttons = [
        [InlineKeyboardButton("✅ START", callback_data=f"start_index#{chat_id}#{last_msg_id}#{skip_count}")],
        [InlineKeyboardButton("❌ CANCEL", callback_data="cancel_index")]
    ]
    await message.reply(
        f"Do you want to start indexing **{channel.title}**?\n"
        f"Total Messages: `{last_msg_id}`\nSkip: `{skip_count}`",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Callback: Start Indexing
@Client.on_callback_query(filters.regex(r"^start_index"))
async def process_index(bot, query):
    _, chat_id, last_msg_id, skip_count = query.data.split("#")
    chat_id, last_msg_id, skip_count = int(chat_id), int(last_msg_id), int(skip_count)
    await query.message.edit("📂 Indexing started...")
    await index_messages_to_db(bot, query.message, chat_id, last_msg_id, skip_count)

# Callback: Cancel Indexing
@Client.on_callback_query(filters.regex(r"^cancel_index"))
async def cancel_index(bot, query):
    temp.CANCEL = True
    await query.message.edit("⚠️ Indexing process has been canceled.")

# Function: Index Messages to Database
async def index_messages_to_db(bot, message, chat_id, last_msg_id, skip_count):
    start_time = time.time()
    total_saved, duplicates, unsupported, errors, skipped = 0, 0, 0, 0, skip_count

    async with lock:
        async for msg in bot.iter_messages(chat_id, last_msg_id, offset=skip_count):
            if temp.CANCEL:
                temp.CANCEL = False
                elapsed_time = get_readable_time(time.time() - start_time)
                return await message.edit(
                    f"✅ Indexing canceled!\n\n"
                    f"⏱️ Time Elapsed: {elapsed_time}\n"
                    f"✅ Saved: {total_saved}\n"
                    f"⚠️ Duplicates: {duplicates}\n"
                    f"🚫 Unsupported: {unsupported}\n"
                    f"❌ Errors: {errors}"
                )

            if not msg.media:
                unsupported += 1
                continue

            media = getattr(msg, msg.media.value, None)
            if not media or media.mime_type not in ["video/mp4", "video/x-matroska"]:
                unsupported += 1
                continue

            save_status = await save_file(media)
            if save_status == "suc":
                total_saved += 1
            elif save_status == "dup":
                duplicates += 1
            elif save_status == "err":
                errors += 1

            skipped += 1
            if skipped % 50 == 0:
                await message.edit(
                    f"📊 Indexing Progress:\n\n"
                    f"✅ Saved: {total_saved}\n"
                    f"⚠️ Duplicates: {duplicates}\n"
                    f"🚫 Unsupported: {unsupported}\n"
                    f"❌ Errors: {errors}\n"
                    f"⏳ Processed: {skipped} / {last_msg_id}"
                )

        elapsed_time = get_readable_time(time.time() - start_time)
        await message.edit(
            f"✅ Indexing completed successfully!\n\n"
            f"⏱️ Time Taken: {elapsed_time}\n"
            f"✅ Saved: {total_saved}\n"
            f"⚠️ Duplicates: {duplicates}\n"
            f"🚫 Unsupported: {unsupported}\n"
            f"❌ Errors: {errors}"
    )
