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
    if lock.locked():
        return await message.reply("🔒 A broadcast is already in progress. Please wait.")

    p = await message.reply("Do you want to pin this message for users?", 
                             reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True))
    msg = await bot.listen(message.chat.id, message.from_user.id)
    is_pin = msg.text.lower() == 'yes'
    await p.delete()

    users = await db.get_all_users()
    b_msg = message.reply_to_message
    b_sts = await message.reply_text("⏳ Starting broadcast to users...")

    start_time = time.time()
    total_users = await db.total_users_count()
    done, success, failed = 0, 0, 0

    async with lock:
        async for user in users:
            if temp.USERS_CANCEL:
                temp.USERS_CANCEL = False
                await b_sts.edit(f"❌ Users broadcast cancelled!\nCompleted: {done}/{total_users}")
                return

            try:
                await bot.send_message(user['id'], b_msg.text, disable_notification=True)
                if is_pin:
                    await bot.pin_chat_message(user['id'], b_msg.id)
                success += 1
            except Exception:
                failed += 1
            done += 1

            # Update Status Every 20 Users
            if done % 20 == 0:
                btn = [[InlineKeyboardButton("CANCEL", callback_data="broadcast_cancel#users")]]
                await b_sts.edit(f"📤 Broadcasting to users...\nCompleted: {done}/{total_users}\nSuccess: {success}\nFailed: {failed}", 
                                 reply_markup=InlineKeyboardMarkup(btn))
                
        time_taken = get_readable_time(time.time() - start_time)
        await b_sts.edit(f"✅ Users broadcast completed!\nTime: {time_taken}\nTotal: {total_users}\nSuccess: {success}\nFailed: {failed}")

# Broadcast to Groups
@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_groups(bot, message):
    p = await message.reply("Do you want to pin this message for groups?", 
                             reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True))
    msg = await bot.listen(message.chat.id, message.from_user.id)
    is_pin = msg.text.lower() == 'yes'
    await p.delete()

    groups = await db.get_all_chats()
    b_msg = message.reply_to_message
    b_sts = await message.reply_text("⏳ Starting broadcast to groups...")

    start_time = time.time()
    total_groups = await db.total_chat_count()
    done, success, failed = 0, 0, 0

    async with lock:
        async for group in groups:
            if temp.GROUPS_CANCEL:
                temp.GROUPS_CANCEL = False
                await b_sts.edit(f"❌ Groups broadcast cancelled!\nCompleted: {done}/{total_groups}")
                return

            try:
                await bot.send_message(group['id'], b_msg.text, disable_notification=True)
                if is_pin:
                    await bot.pin_chat_message(group['id'], b_msg.id)
                success += 1
            except Exception:
                failed += 1
            done += 1

            # Update Status Every 20 Groups
            if done % 20 == 0:
                btn = [[InlineKeyboardButton("CANCEL", callback_data="broadcast_cancel#groups")]]
                await b_sts.edit(f"📤 Broadcasting to groups...\nCompleted: {done}/{total_groups}\nSuccess: {success}\nFailed: {failed}", 
                                 reply_markup=InlineKeyboardMarkup(btn))
                
        time_taken = get_readable_time(time.time() - start_time)
        await b_sts.edit(f"✅ Groups broadcast completed!\nTime: {time_taken}\nTotal: {total_groups}\nSuccess: {success}\nFailed: {failed}")
