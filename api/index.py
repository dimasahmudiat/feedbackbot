import json
import logging
import os
import sys
import requests
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict

# ===== KONFIGURASI =====
BOT_TOKEN = "8590296376:AAHLIzJxaftbJaqO92EZP41p10DRi78XeEY"
CHANNEL_ID = "@dimzmodsofc"  # CHANNEL TUJUAN (GANTI DENGAN CHANNEL ANDA)
ADMIN_ID = 6201552432  # Admin untuk notifikasi (opsional)

# ===== LOGGING =====
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== FUNGSI TELEGRAM =====
def telegram_request(method: str, payload: Dict[str, Any]) -> Dict:
    """Kirim request ke Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Telegram API error: {e}")
        return {"ok": False, "error": str(e)}

def send_message(chat_id: int, text: str, parse_mode: str = "Markdown", keyboard: dict = None) -> Dict:
    """Kirim pesan teks"""
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if keyboard:
        payload["reply_markup"] = keyboard
    return telegram_request("sendMessage", payload)

def copy_message_to_channel(from_chat_id: int, message_id: int) -> Dict:
    """Copy pesan ke channel (lebih baik dari forward)"""
    payload = {
        "chat_id": CHANNEL_ID,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    }
    return telegram_request("copyMessage", payload)

# ===== HANDLER VERCEL =====
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Tampilkan status bot"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bot Feedback Channel</title>
            <style>
                body {{ font-family: Arial; text-align: center; padding: 50px; background: #1a1a1a; color: white; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #2d2d2d; padding: 30px; border-radius: 10px; }}
                .status {{ color: #4CAF50; font-size: 1.2em; }}
                .channel {{ background: #363636; padding: 10px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Bot Feedback Channel</h1>
                <div class="status">✅ BOT AKTIF</div>
                <div class="channel">
                    <strong>Channel Tujuan:</strong> {CHANNEL_ID}<br>
                    <a href="https://t.me/{CHANNEL_ID[1:]}" style="color: #4CAF50;">Kunjungi Channel</a>
                </div>
                <p>Bot akan meneruskan semua pesan ke channel di atas</p>
                <small>Python: {sys.version[:50]}</small>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def do_POST(self):
        """Terima webhook dari Telegram"""
        try:
            # Baca data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data.decode('utf-8'))
            
            logger.info(f"Update: {update.get('update_id')}")
            
            # Proses update
            self.process_update(update)
            
            # Selalu return 200
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error: {e}")
            self.send_response(200)
            self.end_headers()
    
    def process_update(self, update: Dict):
        """Proses update dari Telegram"""
        try:
            message = update.get('message', {})
            if not message:
                return
            
            chat = message.get('chat', {})
            user = message.get('from', {})
            
            user_id = user.get('id')
            username = user.get('username', 'no_username')
            first_name = user.get('first_name', 'User')
            text = message.get('text', '')
            
            # ===== COMMAND /start =====
            if text == '/start':
                welcome = f"""
🎉 *Selamat Datang!* 🎉

Halo {first_name}!

Bot ini adalah bot feedback untuk channel *{CHANNEL_ID}*

📝 *Cara penggunaan:*
Kirim pesan, foto, video, atau file apapun ke bot ini
Maka akan otomatis tampil di channel!

Terima kasih atas partisipasinya! 🙏
                """
                
                keyboard = {
                    "inline_keyboard": [[
                        {"text": "📢 Lihat Channel", "url": f"https://t.me/{CHANNEL_ID[1:]}"}
                    ]]
                }
                
                send_message(user_id, welcome, keyboard=keyboard)
                return
            
            # ===== FORWARD KE CHANNEL =====
            # Cek apakah ini bukan pesan dari channel sendiri
            if str(user_id) != str(CHANNEL_ID).replace('@', ''):
                
                # Copy pesan ke channel
                result = copy_message_to_channel(user_id, message['message_id'])
                
                if result.get('ok'):
                    # Konfirmasi ke pengirim
                    confirm = f"✅ *Pesan berhasil dikirim ke channel*\n\nChannel: {CHANNEL_ID}"
                    send_message(user_id, confirm)
                    
                    # Notifikasi ke admin (opsional)
                    admin_msg = f"""
📨 *Pesan masuk ke channel*
👤 {first_name} (@{username})
🆔 `{user_id}`
📝 Lihat di channel: {CHANNEL_ID}
                    """
                    send_message(ADMIN_ID, admin_msg)
                else:
                    # Gagal - mungkin bot tidak punya akses ke channel
                    error_msg = """
❌ *Gagal mengirim ke channel*

Kemungkinan:
• Bot belum ditambahkan sebagai admin channel
• Channel tidak ditemukan

Hubungi admin untuk memperbaiki
                    """
                    send_message(user_id, error_msg)
                    send_message(ADMIN_ID, f"🚨 ERROR: Bot tidak bisa kirim ke {CHANNEL_ID}. Cek akses bot!")
        
        except Exception as e:
            logger.error(f"Process error: {e}")
