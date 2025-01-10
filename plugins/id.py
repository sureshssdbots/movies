from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

@Client.on_message(filters.command('id'))
async def show_id(client, message):
    try:
        chat_type = message.chat.type
        if chat_type == enums.ChatType.PRIVATE:
            await message.reply_text(
                f"👤 **User ID:** `{message.from_user.id}`"
            )

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            await message.reply_text(
                f"👥 **Group Name:** {message.chat.title}\n🆔 **Group ID:** `{message.chat.id}`"
            )

        elif chat_type == enums.ChatType.CHANNEL:
            await message.reply_text(
                f"📢 **Channel Name:** {message.chat.title}\n🆔 **Channel ID:** `{message.chat.id}`"
            )

    except Exception as e:
        await message.reply_text("⚠️ **Error:** Something went wrong.")
        logger.error(e)

@Client.on_message(filters.command('botinfo'))
async def bot_info(client, message):
    bot = await client.get_me()
    await message.reply_text(
        f"🤖 **Bot Information:**\n"
        f"• Name: {bot.first_name}\n"
        f"• Username: @{bot.username}\n"
        f"• Bot ID: `{bot.id}`"
                                                                            )
