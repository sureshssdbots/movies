import re
import logging
from pyrogram import Client, filters
from info import DELETE_CHANNELS, LOG_CHANNEL
from database.ia_filterdb import Media, unpack_new_file_id

# लॉगिंग सेटअप
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# केवल डाक्यूमेंट, वीडियो, और ऑडियो फ़ाइल्स के लिए फ़िल्टर
media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(DELETE_CHANNELS) & media_filter)
async def delete_multiple_media(bot, message):
    """
    DELETE_CHANNELS में भेजी गई MP4 और MKV फाइल्स को डेटाबेस से हटाने वाला हैंडलर।
    """
    try:
        # मीडिया फाइल को प्राप्त करें
        media = getattr(message, message.media.value, None)
        
        if not media:
            logger.warning(f"No media found in message: {message.message_id}")
            return
        
        # केवल MP4 और MKV फाइल्स के लिए MIME टाइप चेक करें
        if media.mime_type not in ['video/mp4', 'video/x-matroska']:
            logger.info(f"Unsupported file type: {media.mime_type}")
            return
        
        # फाइल ID को अनपैक करें
        file_id, _ = unpack_new_file_id(media.file_id)
        
        # डेटाबेस में फाइल की तलाश करें
        result = await Media.find_one({"file_id": file_id})
        if result:
            # फाइल को डेटाबेस से हटाएं
            await result.delete()
            logger.info(f"File {media.file_name} with ID {file_id} deleted from database.")
        else:
            logger.warning(f"File {media.file_name} with ID {file_id} not found in database.")
    
    except Exception as e:
        # किसी भी एरर को LOG_CHANNEL में भेजें और लॉग करें
        error_message = f"Error processing file in message {message.message_id}: {str(e)}"
        logger.error(error_message)
        await bot.send_message(LOG_CHANNEL, error_message)
