from pyrogram import Client, filters
from info import ADMINS
import re
from database.users_chats_db import db

@Client.on_message(filters.command("set_muc") & filters.user(ADMINS))
async def set_muc_id(client, message):
    try:
        # चेक करें कि कमांड में चैनल ID दी गई है या नहीं
        if len(message.command) < 2:
            return await message.reply("कृपया चैनल ID प्रदान करें। उदाहरण: /set_muc -1001234567890")

        id = message.command[1]
        
        # चैनल ID को वैलिडेट करें कि वह '-100' से शुरू हो और उसकी लंबाई 14 हो
        if id.startswith('-100') and len(id) == 14:
            is_suc = await db.movies_update_channel_id(id)
            if is_suc:
                await message.reply(f"✅ मूवीज़ अपडेट चैनल ID सफलतापूर्वक सेट किया गया: {id}")
            else:
                await message.reply(f"❌ मूवीज़ अपडेट चैनल ID सेट करने में विफल: {id}. कृपया पुनः प्रयास करें।")
        else:
            await message.reply("⚠️ अवैध चैनल ID! यह '-100' से शुरू होना चाहिए और 14 कैरेक्टर लंबी होनी चाहिए।")
    except Exception as e:
        print(f"set_muc_id में एरर: {e}")
        await message.reply(f"❌ मूवीज़ चैनल ID सेट करने में एक त्रुटि हुई है: {str(e)}")
