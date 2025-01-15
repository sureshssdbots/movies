from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
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

        p = await message.reply("Do you want to pin this message for users?",
                                 reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True))
        msg = await bot.listen(message.chat.id, message.from_user.id)
        is_pin = msg.text.lower() == 'yes'
        await p.delete()

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
                    if is_pin:
                        await bot.pin_chat_message(user['id'], b_msg.id)
                    success += 1
                except Exception as e:
                    failed += 1
                    print(f"Error sending message to {user['id']}: {e}")
                done += 1

                if done % 20 == 0:
                    await b_sts.edit(f"📤 Broadcasting to users...\nCompleted: {done}/{total_users}\nSuccess: {success}\nFailed: {failed}",
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("CANCEL", callback_data="broadcast_cancel#users")]]))

            time_taken = get_readable_time(time.time() - start_time)
            await b_sts.edit(f"✅ Broadcast completed!\nTime: {time_taken}\nTotal: {total_users}\nSuccess: {success}\nFailed: {failed}")

    except Exception as e:
        print(f"Broadcast Error: {e}")

# Broadcast to Groups
@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_groups(bot, message):
    try:
        p = await message.reply("Do you want to pin this message for groups?",
                                 reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True))
        msg = await bot.listen(message.chat.id, message.from_user.id)
        is_pin = msg.text.lower() == 'yes'
        await p.delete()

        groups = await db.get_all_chats()
        if not groups:
            return await message.reply("No groups found in the database.")

        b_msg = message.reply_to_message
        if not b_msg:
            return await message.reply("Please reply to a message to broadcast.")

        b_sts = await message.reply_text("⏳ Starting broadcast to groups...")

        start_time = time.time()
        total_groups = len(groups)
        done, success, failed = 0, 0, 0

        async with lock:
            for group in groups:
                if temp.GROUPS_CANCEL:
                    temp.GROUPS_CANCEL = False
                    await b_sts.edit(f"❌ Broadcast cancelled!\nCompleted: {done}/{total_groups}")
                    return

                try:
                    await bot.send_message(group['id'], b_msg.text, disable_notification=True)
                    if is_pin:
                        await bot.pin_chat_message(group['id'], b_msg.id)
                    success += 1
                except Exception as e:
                    failed += 1
                    print(f"Error sending message to {group['id']}: {e}")
                done += 1

                if done % 20 == 0:
                    await b_sts.edit(f"📤 Broadcasting to groups...\nCompleted: {done}/{total_groups}\nSuccess: {success}\nFailed: {failed}",
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("CANCEL", callback_data="broadcast_cancel#groups")]]))

            time_taken = get_readable_time(time.time
