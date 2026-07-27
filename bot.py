from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from music import search_music
from config import TOKEN
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from downloader import download_music
import os

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚔️ 𝐃𝐈𝐋𝐒𝐇𝐎𝐃 𝐌𝐔𝐒𝐈𝐂 ⚔️\n\n"
        "🎵 Добро пожаловать!\n\n"
        "🔎 Отправь название любой песни.\n"
        "📥 Я найду её и отправлю в MP3.\n\n"
        "⚡ Быстро • 🎧 Качественно • 🚀 Бесплатно"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    songs = search_music(update.message.text)

    if not songs:
        await update.message.reply_text("❌ Ничего не найдено.")
        return

    context.user_data["songs"] = songs
    
    def short_title(title):
        if len(title) > 45:
            return title[:42] + "..."
        return title

    keyboard = []

    for i, song in enumerate(songs):
        keyboard.append([
            InlineKeyboardButton(
                f"🎵 {short_title(song['title'])}",
                callback_data=str(i)
            )
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎵 <b>Найдено несколько результатов</b>\n\n"
        "👇 Выбери нужную песню:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    songs = context.user_data.get("songs")

    if not songs:
        await query.message.reply_text(
            "❌ Поиск устарел. Пожалуйста, напиши название песни заново."
        )
        return

    index = int(query.data)

    song = songs[index]

    status = await query.message.reply_text(
        f"🎵 {song['title']}\n\n"
        f"🎧 𝑫𝒊𝒍𝒔𝒉𝒐𝒅 𝑴𝒖𝒔𝒊𝒄\n"
        f"⏱ Длительность: {song['duration']}\n\n"
         "⬇️ Скачиваю..."
    )

    file = download_music(song["videoId"])

    await status.edit_text(
        "🎵 Конвертирую в MP3..."
    )

    await status.edit_text(
        "📤 Отправляю..."
    )

    try:
        with open(file, "rb") as audio:
            await query.message.reply_audio(
                audio=audio,
                title=song["title"],
                performer="𝑫𝒊𝒍𝒔𝒉𝒐𝒅 𝑴𝒖𝒔𝒊𝒄"
            )

            await status.edit_text(
                f"✅ Готово!\n\n"
                f"🎵 {song['title']}\n"
                "🎧 𝑫𝒊𝒍𝒔𝒉𝒐𝒅 𝑴𝒖𝒔𝒊𝒄\n\n"
                "❤️ Приятного прослушивания!"
            )

    finally:
        if os.path.exists(file):
            os.remove(file)

app = (
    Application.builder()
    .token(TOKEN)
    .connect_timeout(30)
    .read_timeout(60)
    .write_timeout(60)
    .build()
)

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

print("🤖 Бот запущен...")

app.add_handler(CallbackQueryHandler(button))

app.run_polling()