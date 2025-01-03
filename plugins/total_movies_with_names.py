from pyrogram import Client, filters
from database.ia_filterdb import Media  # Media डेटाबेस का इम्पोर्ट

# /totalmovies कमांड हैंडलर
@Client.on_message(filters.command("totalmovies") & filters.user([6151975257]))  # Admin ID चेक करें
async def total_movies(client, message):
    try:
        # डेटाबेस से मूवीज़ की कुल संख्या गिनें
        total_movies = await Media.collection.count_documents({})
        movie_list = await Media.collection.find({}, {"file_name": 1}).to_list(length=total_movies)
        
        # फाइल नामों को टेक्स्ट में कन्वर्ट करें
        movie_names = "\n".join([f"- {movie['file_name']}" for movie in movie_list if 'file_name' in movie])

        if movie_names:
            response = (
                f"🎥 **Total Movies in Database:** `{total_movies}`\n\n"
                f"📋 **Movies List:**\n{movie_names}"
            )
        else:
            response = "🎥 **Total Movies in Database:** `0`\n\nNo movies found."

        # उत्तर भेजें
        await message.reply_text(response)

    except Exception as e:
        await message.reply_text(f"❌ **Error:** `{e}`")
