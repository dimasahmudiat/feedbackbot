import json
import logging
import sys
import requests
from http.server import BaseHTTPRequestHandler
from typing import Dict, Any, List

# ===== KONFIGURASI =====
BOT_TOKEN = "8590296376:AAHLIzJxaftbJaqO92EZP41p10DRi78XeEY"

# ===== DAFTAR CHANNEL TUJUAN =====
CHANNELS = [
    "@dimzmodsofc",      # Channel 1
    "@cheatvipdimz"      # Channel 2 (TAMBAHAN)
]

ADMIN_ID = 6201552432  # ID Admin untuk notifikasi

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

def copy_message_to_channel(channel_id: str, from_chat_id: int, message_id: int) -> Dict:
    """Copy pesan ke satu channel"""
    payload = {
        "chat_id": channel_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    }
    return telegram_request("copyMessage", payload)

def copy_message_to_all_channels(from_chat_id: int, message_id: int) -> List[Dict]:
    """Copy pesan ke SEMUA channel sekaligus"""
    results = []
    for channel in CHANNELS:
        try:
            result = copy_message_to_channel(channel, from_chat_id, message_id)
            results.append({
                "channel": channel,
                "success": result.get("ok", False),
                "result": result
            })
            logger.info(f"Kirim ke {channel}: {'✅' if result.get('ok') else '❌'}")
        except Exception as e:
            results.append({
                "channel": channel,
                "success": False,
                "error": str(e)
            })
    return results

# ===== HANDLER VERCEL =====
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Tampilkan status bot dengan daftar channel"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # Buat list channel HTML
        channels_html = ""
        for ch in CHANNELS:
            channels_html += f'<li><a href="https://t.me/{ch[1:]}" target="_blank">{ch}</a> ✅ Aktif</li>'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bot Feedback Multi Channel</title>
            <style>
                body {{ font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
                .container {{ max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }}
                h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
                .status {{ background: #4CAF50; color: white; padding: 10px; border-radius: 5px; display: inline-block; margin-bottom: 20px; }}
                .channels {{ text-align: left; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .channels ul {{ list-style-type: none; padding: 0; }}
                .channels li {{ padding: 10px; margin: 5px 0; background: rgba(255,255,255,0.1); border-radius: 5px; }}
                .channels a {{ color: #FFD700; text-decoration: none; }}
                .footer {{ margin-top: 30px; font-size: 0.8em; opacity: 0.8; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Bot Feedback Multi Channel</h1>
                <div class="status">✅ BOT AKTIF - {len(CHANNELS)} CHANNEL</div>
                
                <div class="channels">
                    <h3>📢 Channel Tujuan:</h3>
                    <ul>
                        {channels_html}
                    </ul>
                </div>
                
                <p>📝 Setiap pesan yang dikirim ke bot akan otomatis tampil di SEMUA channel di atas</p>
                <p>👤 Admin ID: <code>{ADMIN_ID}</code></p>
                
                <div class="footer">
                    Python: {sys.version[:50]}<br>
                    Total Channel: {len(CHANNELS)}
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
    
    def do_POST(self):
        """Terima webhook dari Telegram"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data.decode('utf-8'))
            
            logger.info(f"Update ID: {update.get('update_id')}")
            
            # Proses update
            self.process_update(update)
            
            # Return 200 OK
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
            
            user = message.get('from', {})
            chat = message.get('chat', {})
            
            user_id = user.get('id')
            username = user.get('username', 'no_username')
            first_name = user.get('first_name', 'User')
            text = message.get('text', '')
            
            # ===== COMMAND /start =====
            if text == '/start':
                # Buat daftar channel untuk ditampilkan
                channels_list = "\n".join([f"• {ch}" for ch in CHANNELS])
                
                welcome = f"""
🎉 *Selamat Datang di Bot Feedback!* 🎉

Halo {first_name}! 👋

Bot ini akan meneruskan pesan kamu ke *{len(CHANNELS)} channel* sekaligus:

{channels_list}

📝 *Cara penggunaan:*
Kirim pesan, foto, video, atau file apapun ke bot ini
Maka akan otomatis tampil di SEMUA channel di atas!

Terima kasih atas partisipasinya! 🙏
                """
                
                # Buat tombol untuk semua channel
                buttons = []
                for ch in CHANNELS:
                    buttons.append([{
                        "text": f"📢 {ch}",
                        "url": f"https://t.me/{ch[1:]}"
                    }])
                
                keyboard = {"inline_keyboard": buttons}
                
                send_message(user_id, welcome, keyboard=keyboard)
                return
            
            # ===== FORWARD KE SEMUA CHANNEL =====
            # Cek apakah ini bukan pesan dari bot sendiri
            if str(user_id) != str(BOT_TOKEN).split(':')[0]:
                
                # Kirim ke SEMUA channel
                results = copy_message_to_all_channels(user_id, message['message_id'])
                
                # Hitung sukses dan gagal
                success_count = sum(1 for r in results if r['success'])
                failed_count = len(results) - success_count
                
                # Konfirmasi ke pengirim
                if success_count > 0:
                    confirm = f"""
✅ *Pesan berhasil dikirim!*

📊 *Statistik:*
• Berhasil: {success_count} channel
• Gagal: {failed_count} channel

Terima kasih atas feedbacknya! 🙏
                    """
                    
                    # Tambah daftar channel yang berhasil
                    if success_count > 0:
                        confirm += "\n\n📢 *Channel tujuan:*\n"
                        for r in results:
                            if r['success']:
                                confirm += f"✓ {r['channel']}\n"
                    
                    send_message(user_id, confirm)
                else:
                    error_msg = """
❌ *Gagal mengirim pesan*

Tidak ada channel yang menerima pesan.
Hubungi admin untuk memperbaiki.
                    """
                    send_message(user_id, error_msg)
                
                # Notifikasi ke admin (ringkasan)
                admin_msg = f"""
📨 *Pesan masuk dari user*
👤 {first_name} (@{username})
🆔 `{user_id}`

📊 *Hasil pengiriman ke {len(CHANNELS)} channel:*
✅ Sukses: {success_count}
❌ Gagal: {failed_count}

🔍 Detail:
                """
                
                for r in results:
                    status = "✅" if r['success'] else "❌"
                    admin_msg += f"\n{status} {r['channel']}"
                
                send_message(ADMIN_ID, admin_msg)
        
        except Exception as e:
            logger.error(f"Process error: {e}")
