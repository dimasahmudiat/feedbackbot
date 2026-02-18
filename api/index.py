import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== KONFIGURASI BOT =====
BOT_TOKEN = "8590296376:AAHLIzJxaftbJaqO92EZP41p10DRi78XeEY"
ADMIN_ID = 6201552432
CHANNEL_USERNAME = "@dimzmodsofc"  # Ganti dengan channel Anda

# ===== FUNGSI KIRIM KE TELEGRAM =====
def send_telegram_message(chat_id: int, text: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
    """Kirim pesan teks ke Telegram"""
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Gagal kirim pesan: {e}")
        return {"ok": False, "error": str(e)}

def send_telegram_photo(chat_id: int, photo_id: str, caption: str = "") -> Dict[str, Any]:
    """Kirim foto ke Telegram"""
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_id,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Gagal kirim foto: {e}")
        return {"ok": False, "error": str(e)}

def send_telegram_video(chat_id: int, video_id: str, caption: str = "") -> Dict[str, Any]:
    """Kirim video ke Telegram"""
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    payload = {
        "chat_id": chat_id,
        "video": video_id,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Gagal kirim video: {e}")
        return {"ok": False, "error": str(e)}

def send_telegram_document(chat_id: int, document_id: str, caption: str = "") -> Dict[str, Any]:
    """Kirim dokumen ke Telegram"""
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    payload = {
        "chat_id": chat_id,
        "document": document_id,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Gagal kirim dokumen: {e}")
        return {"ok": False, "error": str(e)}

def send_telegram_audio(chat_id: int, audio_id: str, caption: str = "") -> Dict[str, Any]:
    """Kirim audio ke Telegram"""
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
    payload = {
        "chat_id": chat_id,
        "audio": audio_id,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Gagal kirim audio: {e}")
        return {"ok": False, "error": str(e)}

def send_telegram_voice(chat_id: int, voice_id: str, caption: str = "") -> Dict[str, Any]:
    """Kirim voice ke Telegram"""
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice"
    payload = {
        "chat_id": chat_id,
        "voice": voice_id,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Gagal kirim voice: {e}")
        return {"ok": False, "error": str(e)}

def send_telegram_location(chat_id: int, latitude: float, longitude: float) -> Dict[str, Any]:
    """Kirim lokasi ke Telegram"""
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendLocation"
    payload = {
        "chat_id": chat_id,
        "latitude": latitude,
        "longitude": longitude
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Gagal kirim lokasi: {e}")
        return {"ok": False, "error": str(e)}

# ===== HANDLER UTAMA VERCEL =====
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handler untuk GET request"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bot Feedback Channel</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
                .container {{ max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }}
                h1 {{ font-size: 2.5em; margin-bottom: 20px; }}
                .status {{ background: #4CAF50; color: white; padding: 10px; border-radius: 5px; display: inline-block; }}
                .info {{ margin-top: 30px; text-align: left; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Bot Feedback Channel</h1>
                <div class="status">✅ BOT AKTIF & STABIL</div>
                <div class="info">
                    <p><strong>Channel:</strong> {CHANNEL_USERNAME}</p>
                    <p><strong>Admin ID:</strong> {ADMIN_ID}</p>
                    <p><strong>Python Version:</strong> {sys.version}</p>
                    <p><strong>Status:</strong> Siap menerima pesan!</p>
                </div>
                <p>Kirim pesan ke bot Telegram untuk testing</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def do_POST(self):
        """Handler untuk POST request dari Telegram"""
        try:
            # Baca data dari Telegram
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data.decode('utf-8'))
            
            logger.info(f"Received update: {json.dumps(update)[:200]}...")
            
            # Proses update
            success = self.process_update(update)
            
            # Selalu return 200 ke Telegram
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            # Tetap return 200 agar Telegram tidak mengirim ulang
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True, 'error': str(e)}).encode('utf-8'))
    
    def process_update(self, update: Dict[str, Any]) -> bool:
        """Proses update dari Telegram"""
        try:
            # Ambil informasi pesan
            message = update.get('message', {})
            chat = message.get('chat', {})
            user = message.get('from', {})
            
            user_id = user.get('id', 0)
            username = user.get('username', 'no_username')
            first_name = user.get('first_name', 'User')
            text = message.get('text', '')
            
            # Handle /start command
            if text == '/start':
                welcome_text = f"""
🎉 *Selamat Datang di Bot Feedback Channel!* 🎉

Halo {first_name}! 👋

Bot ini dibuat untuk mengirim feedback ke channel *{CHANNEL_USERNAME}*

📝 *Fitur:*
• Kirim teks, foto, video, dokumen
• Audio, voice note, lokasi
• Auto-forward ke admin

📌 *Cara pakai:*
Kirim langsung pesan kamu ke bot ini!
                """
                
                keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "📢 Lihat Channel", "url": f"https://t.me/{CHANNEL_USERNAME[1:]}"},
                            {"text": "📞 Admin", "url": f"tg://user?id={ADMIN_ID}"}
                        ]
                    ]
                }
                
                # Kirim pesan dengan keyboard
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": user_id,
                    "text": welcome_text,
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
                
                import requests
                requests.post(url, json=payload, timeout=10)
                return True
            
            # Untuk pesan biasa, forward ke admin
            if user_id != ADMIN_ID:  # Jangan forward pesan admin ke diri sendiri
                # Header untuk admin
                header = f"""
📨 *FEEDBACK BARU*
👤 {first_name} (@{username})
🆔 `{user_id}`
━━━━━━━━━━━━━━━━
                """
                
                # Cek jenis pesan
                if 'text' in message:
                    # Pesan teks
                    send_telegram_message(ADMIN_ID, f"{header}\n💬 *Pesan:*\n{text}")
                    
                elif 'photo' in message:
                    # Pesan foto
                    photo = message['photo'][-1]['file_id']
                    caption = message.get('caption', 'Tidak ada caption')
                    send_telegram_photo(ADMIN_ID, photo, f"{header}\n📷 *Foto*\n📝 *Caption:* {caption}")
                    
                elif 'video' in message:
                    # Pesan video
                    video = message['video']['file_id']
                    caption = message.get('caption', 'Tidak ada caption')
                    send_telegram_video(ADMIN_ID, video, f"{header}\n🎥 *Video*\n📝 *Caption:* {caption}")
                    
                elif 'document' in message:
                    # Pesan dokumen
                    document = message['document']['file_id']
                    caption = message.get('caption', 'Tidak ada caption')
                    send_telegram_document(ADMIN_ID, document, f"{header}\n📎 *Dokumen*\n📝 *Caption:* {caption}")
                    
                elif 'audio' in message:
                    # Pesan audio
                    audio = message['audio']['file_id']
                    caption = message.get('caption', 'Tidak ada caption')
                    send_telegram_audio(ADMIN_ID, audio, f"{header}\n🎵 *Audio*\n📝 *Caption:* {caption}")
                    
                elif 'voice' in message:
                    # Pesan voice
                    voice = message['voice']['file_id']
                    send_telegram_voice(ADMIN_ID, voice, f"{header}\n🎤 *Voice Note*")
                    
                elif 'location' in message:
                    # Pesan lokasi
                    lat = message['location']['latitude']
                    lon = message['location']['longitude']
                    send_telegram_location(ADMIN_ID, lat, lon)
                    send_telegram_message(ADMIN_ID, f"{header}\n📍 *Lokasi*")
                
                # Konfirmasi ke pengirim
                send_telegram_message(user_id, "✅ *Pesan diterima!* Admin akan segera merespon. Terima kasih! 🙏")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in process_update: {e}")
            return False
