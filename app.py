import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Environment variables se credentials uthayenge
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID")
RECIPIENT_PHONE = os.environ.get("RECIPIENT_PHONE")  # WhatsApp Channel ya number

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    
    if "channel_post" in data:
        post = data["channel_post"]
        caption = post.get("caption", post.get("text", ""))
        
        # 1. Agar Photo hai
        if "photo" in post:
            file_id = post["photo"][-1]["file_id"]  # Sabse highest resolution photo
            media_url = get_telegram_file_url(file_id)
            send_whatsapp_media(media_url, caption, "image")
            
        # 2. Agar Video hai
        elif "video" in post:
            file_id = post["video"]["file_id"]
            media_url = get_telegram_file_url(file_id)
            send_whatsapp_media(media_url, caption, "video")
            
        # 3. Agar sirf Text hai
        elif "text" in post:
            send_whatsapp_text(post["text"])
            
    return "OK", 200

def get_telegram_file_url(file_id):
    # Telegram API se file ka path nikalna
    r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}").json()
    file_path = r["result"]["file_path"]
    return f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"

def send_whatsapp_text(text):
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_PHONE,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, json=payload, headers=headers)

def send_whatsapp_media(media_url, caption, media_type):
    url = f"https://graph.cloud.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_PHONE,
        "type": media_type,
        media_type: {
            "link": media_url,
            "caption": caption
        }
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
