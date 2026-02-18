import os
import json
import logging
import asyncio
from http.server import BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# ===== KONFIGURASI =====
TOKEN = "8590296376:AAHLIzJxaftbJaqO92EZP41p10DRi78XeEY"
ADMIN_ID = 6201552432
CHANNEL_ID = "@dimzmodsofc"  # SUDAH DIGANTI DENGAN CHANNEL ANDA

# ===== LOGGING =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Inisialisasi Application
application = Application.builder().token(TOKEN).build()

# ===== HANDLER FUNCTIONS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk perintah /start"""
    user = update.effective_user
    
    welcome_msg = f"""
🎉 *Selamat Datang di Bot Feedback Channel!* 🎉

Halo {user.first_name}! 👋

Bot ini dibuat khusus untuk mengirim feedback ke channel kami. 
Kamu bisa mengirim berbagai jenis konten:

📝 *Fitur yang tersedia:*
• 📷 Foto dengan caption
• 🎥 Video dengan caption
• 📎 File dokumen
• 🎵 Audio / Voice Note
• 📍 Lokasi
• 💬 Teks biasa

📌 *Cara menggunakan:*
Kirim langsung pesan/feedback kamu ke bot ini, 
dan akan langsung diteruskan ke admin channel!

Terima kasih atas partisipasinya! 🙏
"""
    
    keyboard = [
        [InlineKeyboardButton("📢 Lihat Channel", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")],
        [InlineKeyboardButton("📞 Hubungi Admin", url=f"tg://user?id={ADMIN_ID}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk semua jenis pesan"""
    user = update.effective_user
    user_id = user.id
    username = user.username or "Tidak ada username"
    first_name = user.first_name
    
    # Konfirmasi ke pengirim
    await update.message.reply_text(
        "✅ *Pesan kamu telah diterima dan akan diteruskan ke admin!*\nTerima kasih atas feedbacknya 🙏",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Header pesan untuk admin
    header = f"""
📨 *PESAN FEEDBACK BARU*
━━━━━━━━━━━━━━━━
👤 *Nama:* {first_name}
🆔 *User ID:* `{user_id}`
👥 *Username:* @{username if username != 'Tidak ada username' else '-'}
━━━━━━━━━━━━━━━━
"""
    
    try:
        # KIRIM KE ADMIN
        if update.message.text:
            caption = f"{header}\n💬 *Pesan:*\n{update.message.text}"
            await context.bot.send_message(chat_id=ADMIN_ID, text=caption, parse_mode=ParseMode.MARKDOWN)
            
        elif update.message.photo:
            photo = update.message.photo[-1]
            caption_text = update.message.caption or "Tidak ada caption"
            caption = f"{header}\n📷 *Foto*\n📝 *Caption:* {caption_text}"
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo.file_id, caption=caption, parse_mode=ParseMode.MARKDOWN)
            
        elif update.message.video:
            caption_text = update.message.caption or "Tidak ada caption"
            caption = f"{header}\n🎥 *Video*\n📝 *Caption:* {caption_text}"
            await context.bot.send_video(chat_id=ADMIN_ID, video=update.message.video.file_id, caption=caption, parse_mode=ParseMode.MARKDOWN)
            
        elif update.message.document:
            caption_text = update.message.caption or "Tidak ada caption"
            caption = f"{header}\n📎 *Dokumen*\n📝 *Caption:* {caption_text}"
            await context.bot.send_document(chat_id=ADMIN_ID, document=update.message.document.file_id, caption=caption, parse_mode=ParseMode.MARKDOWN)
            
        elif update.message.audio:
            caption_text = update.message.caption or "Tidak ada caption"
            caption = f"{header}\n🎵 *Audio*\n📝 *Caption:* {caption_text}"
            await context.bot.send_audio(chat_id=ADMIN_ID, audio=update.message.audio.file_id, caption=caption, parse_mode=ParseMode.MARKDOWN)
            
        elif update.message.voice:
            caption = f"{header}\n🎤 *Voice Note*"
            await context.bot.send_voice(chat_id=ADMIN_ID, voice=update.message.voice.file_id, caption=caption, parse_mode=ParseMode.MARKDOWN)
            
        elif update.message.location:
            location = update.message.location
            await context.bot.send_location(chat_id=ADMIN_ID, latitude=location.latitude, longitude=location.longitude)
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"{header}\n📍 *Lokasi*", parse_mode=ParseMode.MARKDOWN)
            
        else:
            await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=user_id, message_id=update.message.message_id)
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"{header}\n🔄 *Pesan Diteruskan*", parse_mode=ParseMode.MARKDOWN)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Maaf, terjadi kesalahan. Silakan coba lagi.")

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.ALL, handle_message))

# ===== VERCEL HANDLER =====
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # Parse update dari Telegram
            update = Update.de_json(json.loads(post_data.decode('utf-8')), application.bot)
            
            # Proses update
            asyncio.run(application.process_update(update))
            
            # Kirim response sukses
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'error'}).encode('utf-8'))
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'''
        <html>
            <head><title>Bot Feedback</title></head>
            <body>
                <h1>🤖 Bot Feedback Aktif!</h1>
                <p>Bot berjalan normal.</p>
                <p>Channel: @dimzmodsofc</p>
            </body>
        </html>
        ''')
