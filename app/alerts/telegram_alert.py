import requests

# =========================
# 🔑 CONFIG (IMPORTANT)
# =========================
BOT_TOKEN = "8790668637:AAHPYHjBWLxZL2-dkt936qwqi4pRkdW5pEI"   # ⚠️ Replace with new token
CHAT_ID = "5584355303"           # ⚠️ Keep as STRING

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# 📩 SEND TEXT MESSAGE
# =========================
def send_telegram_alert(message):
    try:
        url = f"{BASE_URL}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"   # optional formatting
        }

        response = requests.post(url, data=payload)

        if response.status_code == 200:
            print("✅ Telegram message sent")
        else:
            print("❌ Message failed:", response.text)

    except Exception as e:
        print("❌ Telegram message error:", e)


# =========================
# 📸 SEND PHOTO
# =========================
def send_telegram_photo(image_path):
    try:
        url = f"{BASE_URL}/sendPhoto"

        with open(image_path, "rb") as photo:
            files = {"photo": photo}
            data = {"chat_id": CHAT_ID}

            response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            print("✅ Telegram photo sent")
        else:
            print("❌ Photo failed:", response.text)

    except FileNotFoundError:
        print("❌ Image file not found:", image_path)

    except Exception as e:
        print("❌ Telegram photo error:", e)


# =========================
# 🧪 TEST FUNCTION
# =========================
if __name__ == "__main__":
    print("🚀 Testing Telegram...")

    send_telegram_alert("✅ Telegram test message from Focus Guard AI")

    # Test image (make sure file exists)
    test_image = "test.jpg"
    send_telegram_photo(test_image)