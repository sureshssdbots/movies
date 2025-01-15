from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import time
from database.users_chats_db import db
from utils import temp, get_readable_time
from info import ADMINS

lock = asyncio.Lock()

# Cancel Broadcast
@Client.on_callback_query(filters.regex(r'^broadcast_cancel'))
async def broadcast_cancel(bot, query):
    _, ident = query.data.split("#")
    if ident == 'users':
        temp.USERS_CANCEL = True
        await query.message.edit("❌ Users Broadcast Cancelled!")
    elif ident == 'groups':
        temp.GROUPS_CANCEL = True
        await query.message.edit("❌ Groups Broadcast Cancelled!")

# Broadcast to Users
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_users(bot, message):
    try:
        if lock.locked():
            return await message.reply("🔒 A broadcast is already in progress. Please wait.")

        users = await db.get_all_users()
        if not users:
            return await message.reply("No users found in the database.")

        b_msg = message.reply_to_message
        if not b_msg:
            return await message.reply("Please reply to a message to broadcast.")

        b_sts = await message.reply_text("⏳ Starting broadcast to users...")
        start_time = time.time()

        total_users = len(users)
        done, success, failed = 0, 0, 0

        async with lock:
            for user in users:
                if temp.USERS_CANCEL:
                    temp.USERS_CANCEL = False
                    await b_sts.edit(f"❌ Broadcast cancelled!\nCompleted: {done}/{total_users}")
                    return

                try:
                    await bot.send_message(user['id'], b_msg.text, disable_notification=True)
                    success += 1
                except Exception as e:
                    failed += 1
                    print(f"Error sending message to {user['id']}: {e}")
                done += 1

                if done % 20 == 0:
                    await b_sts.edit(f"📤 Broadcasting...\nCompleted: {done}/{total_users}\nSuccess: {success}\nFailed: {failed}",
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("CANCEL", callback_data="broadcast_cancel#users")]]))

            time_taken = get_readable_time(time.time() - start_time)
            await b_sts.edit(f"✅ Broadcast completed!\nTime: {time_taken}\nTotal: {total_users}\nSuccess: {success}\nFailed: {failed}")

    except Exception as e:
        print(f"Broadcast Error: {e}")
