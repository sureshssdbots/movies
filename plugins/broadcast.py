from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from utils import temp, get_readable_time

lock = asyncio.Lock()


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_users(bot, message):
    if lock.locked():
        return await message.reply("A broadcast is already in progress. Please wait until it's completed.")
    
    # Broadcast को Pin करने का विकल्प
    p_msg = await message.reply("<b>Do you want to pin this message for users?</b>", reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True))
    user_response = await bot.listen(chat_id=message.chat.id, user_id=message.from_user.id)
    is_pin = user_response.text.lower() == "yes"
    await p_msg.delete()
    
    users = await db.get_all_users()
    total_users = len(users)
    start_time = asyncio.get_running_loop().time()
    success, failed, done = 0, 0, 0

    status_message = await message.reply(f"<b>Broadcasting message to users...</b>")

    async with lock:
        for user in users:
            try:
                if temp.USERS_CANCEL:
                    temp.USERS_CANCEL = False
                    await status_message.edit(
                        f"Broadcast canceled!\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>"
                    )
                    return
                
                # संदेश भेजने की कोशिश
                await bot.copy_message(
                    chat_id=int(user["id"]),
                    from_chat_id=message.chat.id,
                    message_id=message.reply_to_message.message_id
                )
                success += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                failed += 1
            
            done += 1
            if done % 20 == 0:  # हर 20 संदेशों के बाद अपडेट करें
                await status_message.edit(
                    f"Broadcast in progress...\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("CANCEL", callback_data="broadcast_cancel#users")]]
                    )
                )

        total_time = get_readable_time(asyncio.get_running_loop().time() - start_time)
        await status_message.edit(
            f"Broadcast completed in {total_time}.\n\nTotal Users: <code>{total_users}</code>\nCompleted: <code>{done}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>"
        )


@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_groups(bot, message):
    if lock.locked():
        return await message.reply("A broadcast is already in progress. Please wait until it's completed.")
    
    # Broadcast को Pin करने का विकल्प
    p_msg = await message.reply("<b>Do you want to pin this message for groups?</b>", reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True, resize_keyboard=True))
    user_response = await bot.listen(chat_id=message.chat.id, user_id=message.from_user.id)
    is_pin = user_response.text.lower() == "yes"
    await p_msg.delete()
    
    groups = await db.get_all_chats()
    total_groups = len(groups)
    start_time = asyncio.get_running_loop().time()
    success, failed, done = 0, 0, 0

    status_message = await message.reply(f"<b>Broadcasting message to groups...</b>")

    async with lock:
        for group in groups:
            try:
                if temp.GROUPS_CANCEL:
                    temp.GROUPS_CANCEL = False
                    await status_message.edit(
                        f"Broadcast canceled!\n\nTotal Groups: <code>{total_groups}</code>\nCompleted: <code>{done}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>"
                    )
                    return
                
                # संदेश भेजने की कोशिश
                await bot.copy_message(
                    chat_id=int(group["id"]),
                    from_chat_id=message.chat.id,
                    message_id=message.reply_to_message.message_id
                )
                success += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                failed += 1
            
            done += 1
            if done % 20 == 0:  # हर 20 संदेशों के बाद अपडेट करें
                await status_message.edit(
                    f"Broadcast in progress...\n\nTotal Groups: <code>{total_groups}</code>\nCompleted: <code>{done}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("CANCEL", callback_data="broadcast_cancel#groups")]]
                    )
                )

        total_time = get_readable_time(asyncio.get_running_loop().time() - start_time)
        await status_message.edit(
            f"Broadcast completed in {total_time}.\n\nTotal Groups: <code>{total_groups}</code>\nCompleted: <code>{done}</code>\nSuccess: <code>{success}</code>\nFailed: <code>{failed}</code>"
)
                


