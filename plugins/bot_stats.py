from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from info import ADMINS, LOG_CHANNEL, USERNAME
from database.users_chats_db import db
from database.ia_filterdb import Media, get_files_db_size
from utils import get_size, temp
from Script import script
from datetime import datetime
import psutil
import time

# New Group Join Event (Custom Message & Logs)
@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    check = [u.id for u in message.new_chat_members]
    if temp.ME in check:
        if (str(message.chat.id)).startswith("-100") and not await db.get_chat(message.chat.id):
            total = await bot.get_chat_members_count(message.chat.id)
            user = message.from_user.mention if message.from_user else "Dear"
            group_link = await message.chat.export_invite_link()

            # Customizing New Group Join Log Message
            await bot.send_message(
                LOG_CHANNEL, 
                script.NEW_GROUP_TXT.format(temp.B_LINK, message.chat.title, message.chat.id, message.chat.username, group_link, total, user),
                disable_web_page_preview=True
            )
            await db.add_chat(message.chat.id, message.chat.title, datetime.now())

            # Custom Inline Button and Message to User
            btn = [[InlineKeyboardButton('⚡️ सᴜᴘᴘᴏʀᴛ ⚡️', url=USERNAME)]]
            reply_markup = InlineKeyboardMarkup(btn)

            await bot.send_message(
                chat_id=message.chat.id,
                text=f"<b>☤ धन्यवाद {message.chat.title} में मुझे जोड़ने के लिए!\n\n🤖 मुझे एडमिन बनाना न भूलें।</b>",
                reply_markup=reply_markup
            )

# Command to Leave a Group (with reason)
@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    r = message.text.split(None)
    if len(message.command) == 1:
        return await message.reply('<b>उपयोग करें: /leave -100******</b>')

    chat = message.command[1]
    reason = "कोई कारण नहीं बताया"

    # Checking the reason if present
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        
    try:
        chat = int(chat)
    except:
        chat = chat

    try:
        btn = [[InlineKeyboardButton('⚡️ ᴏᴡɴᴇʀ ⚡️', url=USERNAME)]]
        reply_markup = InlineKeyboardMarkup(btn)
        
        await bot.send_message(
            chat_id=chat,
            text=f'😞 मुझे इस ग्रुप से निकाल दिया गया है। कारण: {reason}',
            reply_markup=reply_markup,
        )
        await bot.leave_chat(chat)
        await db.delete_chat(chat)

        await message.reply(f"<b>सफलतापूर्वक {chat} से छोड़ दिया गया।</b>")
    except Exception as e:
        await message.reply(f'<b>त्रुटि - `{e}`</b>')

# Command to List all Groups in the Database
@Client.on_message(filters.command('groups') & filters.user(ADMINS))
async def groups_list(bot, message):
    msg = await message.reply('<b>सर्च हो रहा है...</b>')
    chats = await db.get_all_chats()
    out = "सभी ग्रुप्स:\n\n"
    count = 1

    async for chat in chats:
        chat_info = await bot.get_chat(chat['id'])
        members_count = chat_info.members_count if chat_info.members_count else "अज्ञात"
        out += f"<b>{count}. नाम - `{chat['title']}`\nID - `{chat['id']}`\nसदस्य - `{members_count}`</b>\n\n"
        count += 1

    try:
        if count > 1:
            await msg.edit_text(out)
        else:
            await msg.edit_text("<b>कोई ग्रुप नहीं पाया गया।</b>")
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="<b>सभी ग्रुप्स की लिस्ट</b>")

# Command for Bot Stats (CPU, Memory, Database Size)
@Client.on_message(filters.command('stats') & filters.user(ADMINS) & filters.incoming)
async def get_ststs(bot, message):
    users = await db.total_users_count()
    groups = await db.total_chat_count()
    size = get_size(await db.get_db_size())
    free = get_size(536870912)
    files = await Media.count_documents()
    db2_size = get_size(await get_files_db_size())
    db2_free = get_size(536870912)
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - time.time()))
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent()

    # Customizing Status Message
    await message.reply_text(script.STATUS_TXT.format(users, groups, size, free, files, db2_size, db2_free, uptime, ram, cpu))

# Command to Get Help / FAQ
@Client.on_message(filters.command('help'))
async def help_command(bot, message):
    help_text = """
    <b>Welcome to the bot! Here are some commands:</b>
    /leave - Leave a group
    /groups - List all saved groups
    /stats - Get bot status
    /help - Get help on commands
    """
    await message.reply_text(help_text)
