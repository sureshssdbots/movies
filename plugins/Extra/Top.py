from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup
from info import ADMINS, DATABASE_URI
import asyncio
from database.topdb import JsTopDB

movie_series_db = JsTopDB(DATABASE_URI)

# set list of movie and series names (add/remove/update)
@Client.on_message(filters.command("setlist") & filters.private & filters.user(ADMINS))
async def set_movie_series_names_command(client, message):
    try:
        command, action, *names = message.text.split(maxsplit=2)
    except ValueError:
        await message.reply("Please provide valid parameters for the command.")
        return

    if action == "remove":
        name_to_remove = names[0]
        await movie_series_db.remove_movie_series(name_to_remove)
        await message.reply(f"The movie/series {name_to_remove} has been removed.")
    elif action == "update":
        old_name, new_name = names
        await movie_series_db.update_movie_series(old_name, new_name)
        await message.reply(f"The movie/series {old_name} has been updated to {new_name}.")
    else:
        # existing logic for setting new names
        names_string = ", ".join(names)
        await movie_series_db.set_movie_series_names(names_string, 1)
        await message.reply(f"The movie/series list has been updated successfully.")

# fetch movie and series names based on rank
@Client.on_message(filters.command("trendlist"))
async def get_movie_series_names_command(client, message):
    current_names = await movie_series_db.get_movie_series_names_sorted_by_rank()

    if current_names:
        response = "<b><u>Top Trending List (Based on Ranking):</u></b>\n"
        for i, name in enumerate(current_names, start=1):
            response += f"{i}. {name['name']} - {name['points']} points\n"
        await message.reply(response.strip())
    else:
        await message.reply("The list of top trending movies/series is empty ❌")

# clear movie and series names
@Client.on_message(filters.command("clearlist") & filters.private & filters.user(ADMINS))
async def clear_movie_series_names_command(client, message):
    await movie_series_db.clear_movie_series_names(1)
    await message.reply("The top trending list has been cleared successfully ✅")

# show the top trending movies/series with pagination (showing first 5 results)
@Client.on_message(filters.command("trend"))
async def trending_command(client, message):
    movie_series_names = await movie_series_db.get_movie_series_names_sorted_by_rank()
    
    if not movie_series_names:
        await message.reply("There are no movies or series available for trending.")
        return

    buttons = [[name['name']] for name in movie_series_names[:5]]  # Show first 5 names

    spika = ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True
    )
    m = await message.reply_text("Please wait, fetching top trending...")
    await m.delete()        
    await message.reply("<b>Here is the top trending list 👇</b>", reply_markup=spika)

# set trending list (movie/series names) for suggestion
@Client.on_message(filters.command("setlist") & filters.private & filters.user(ADMINS))
async def set_movie_series_names_command(client, message):
    try:
        command, *names = message.text.split(maxsplit=1)
    except ValueError:
        await message.reply("Please provide a list of movie and series names after the command.")
        return

    if not names:
        await message.reply("Please provide a list of movie and series names after the command.")
        return

    names_string = " ".join(names)

    capitalized_names = ", ".join(" ".join(word.capitalize() for word in name.split()) for name in names_string.split(','))

    await movie_series_db.set_movie_series_names(capitalized_names, 1)

    await message.reply("The list of movie and series names for the suggestion has been updated successfully ✅")

# get movie/series names and show them in a message
@Client.on_message(filters.command("trendlist"))
async def get_movie_series_names_command(client, message):
    current_names = await movie_series_db.get_movie_series_names(1)

    if current_names:
        response = "<b><u>Current List of Top Trending:</u></b>\n"
        for i, name in enumerate(current_names, start=1):
            response += f"{i}. {name}\n"
        await message.reply(response.strip())
    else:
        await message.reply("The list of top trending for buttons are empty ❌")
