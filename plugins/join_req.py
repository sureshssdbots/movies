from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest, InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from info import ADMINS, AUTH_CHANNEL, LOG_CHANNEL

# Handle Join Requests with Auto Approval and Welcome Message
@Client.on_chat_join_request(filters.chat(AUTH_CHANNEL))
async def handle_join_request(client, join_request: ChatJoinRequest):
    user_id = join_request.from_user.id
    if not await db.find_join_req(user_id):
        await db.add_join_req(user_id)
        await join_request.approve()
        
        # Send Welcome Message
        await client.send_message(
            user_id,
            f"🎉 Welcome to {AUTH_CHANNEL}!\n\nWe’re glad to have you here. Please follow the rules and enjoy!"
        )
        
        # Log Join Request in a Channel
        username = join_request.from_user.username or "No Username"
        await client.send_message(
            LOG_CHANNEL,
            f"✅ New member joined:\n\n"
            f"👤 **Name:** {join_request.from_user.first_name}\n"
            f"🔗 **Username:** @{username}\n"
            f"🆔 **User ID:** `{user_id}`"
        )
        print(f"✅ Approved and welcomed user: {user_id}")

# Command to Delete All Join Requests Data from the Database
@Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMINS))
async def delete_requests(client, message):
    await db.del_join_req()
    await message.reply("<b>✅ Successfully cleared all join requests data from the database.</b>")

# Command to Check Total Join Requests Processed
@Client.on_message(filters.command("reqcount") & filters.private & filters.user(ADMINS))
async def request_count(client, message):
    count = await db.get_request_count()  # Function to get total requests count
    await message.reply(f"📊 Total Join Requests Processed: {count}")

# Auto Decline Pending Requests After 24 Hours
import asyncio
import time

async def auto_decline_pending_requests(client):
    while True:
        pending_requests = await db.get_pending_requests()  # Fetch pending requests
        for request in pending_requests:
            user_id, request_time = request['user_id'], request['time']
            if (time.time() - request_time) > 24 * 60 * 60:  # 24 hours
                await client.decline_chat_join_request(AUTH_CHANNEL, user_id)
                await db.remove_request(user_id)  # Remove from database
                print(f"❌ Auto-declined request for user: {user_id}")
        await asyncio.sleep(3600)  # Check every hour

# Multi-Channel Join Request Support
AUTH_CHANNELS = [-1001234567890, -1009876543210]  # Replace with your channel IDs

@Client.on_chat_join_request(filters.chat(AUTH_CHANNELS))
async def handle_multiple_channel_requests(client, join_request: ChatJoinRequest):
    channel_id = join_request.chat.id
    user_id = join_request.from_user.id
    if not await db.find_join_req(user_id):
        await db.add_join_req(user_id)
        await join_request.approve()
        print(f"✅ Approved user {user_id} for channel {channel_id}")
