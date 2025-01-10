from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from plugins.helper.fotnt_string import Fonts

# फ़ॉन्ट स्टाइल बटन दिखाने वाली फ़ंक्शन
@Client.on_message(filters.private & filters.command(["font"]))
async def style_buttons(c, m, cb=False):
    buttons = [
        [
            InlineKeyboardButton('𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛', callback_data='style+typewriter'),
            InlineKeyboardButton('𝕆𝕦𝕥𝕝𝕚𝕟𝕖', callback_data='style+outline'),
            InlineKeyboardButton('𝐒𝐞𝐫𝐢𝐟', callback_data='style+serif'),
        ],
        [
            InlineKeyboardButton('𝑺𝒆𝒓𝒊𝒇', callback_data='style+bold_cool'),
            InlineKeyboardButton('𝑆𝑒𝑟𝑖𝑓', callback_data='style+cool'),
            InlineKeyboardButton('Sᴍᴀʟʟ Cᴀᴘs', callback_data='style+small_cap'),
        ],
        [
            InlineKeyboardButton('𝓈𝒸𝓇𝒾𝓅𝓉', callback_data='style+script'),
            InlineKeyboardButton('𝓼𝓬𝓻𝓲𝓹𝓽', callback_data='style+script_bolt'),
            InlineKeyboardButton('ᵗⁱⁿʸ', callback_data='style+tiny'),
        ],
        [
            InlineKeyboardButton('Next ➡️', callback_data="nxt")
        ]
    ]
    
    if not cb:
        if ' ' in m.text:
            title = m.text.split(" ", 1)[1]
            await m.reply_text(title, reply_markup=InlineKeyboardMarkup(buttons), reply_to_message_id=m.id)
        else:
            await m.reply_text(text="कृपया टेक्स्ट दर्ज करें, जैसे: `/font [text]`")    
    else:
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))

# 'Next' बटन के लिए फ़ंक्शन
@Client.on_callback_query(filters.regex('^nxt'))
async def nxt(c, m):
    if m.data == "nxt":
        buttons = [
            [
                InlineKeyboardButton('🇸 🇵 🇪 🇨 🇮 🇦 🇱 ', callback_data='style+special'),
                InlineKeyboardButton('🅂🅀🅄🄰🅁🄴🅂', callback_data='style+squares'),
                InlineKeyboardButton('🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎', callback_data='style+squares_bold'),
            ],
            [
                InlineKeyboardButton('ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ', callback_data='style+andalucia'),
                InlineKeyboardButton('爪卂几ᘜ卂', callback_data='style+manga'),
                InlineKeyboardButton('S̾t̾i̾n̾k̾y̾', callback_data='style+stinky'),
            ],
            [
                InlineKeyboardButton('⬅️ Back', callback_data='nxt+0')
            ]
        ]
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))

# फ़ॉन्ट स्टाइल को लागू करने वाली मुख्य फ़ंक्शन
@Client.on_callback_query(filters.regex('^style'))
async def style(c, m):
    await m.answer()
    cmd, style = m.data.split('+')

    # स्टाइल के आधार पर फ़ॉन्ट्स को चुनें
    font_map = {
        'typewriter': Fonts.typewriter,
        'outline': Fonts.outline,
        'serif': Fonts.serief,
        'bold_cool': Fonts.bold_cool,
        # यहाँ पर सभी स्टाइल्स की लिस्ट ऐड करें...
    }

    cls = font_map.get(style)

    if cls:
        r, oldtxt = m.message.reply_to_message.text.split(None, 1)
        new_text = cls(oldtxt)
        try:
            await m.message.edit_text(f"`{new_text}`\n\n👆 क्लिक करें कॉपी करने के लिए", reply_markup=m.message.reply_markup)
        except Exception as e:
            print(e)
