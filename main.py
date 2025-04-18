from flask import Flask
from threading import Thread
import asyncio
import random
import string
import aiohttp

# إعدادات بوت تيليجرام
TELEGRAM_BOT_TOKEN = "7523059933:AAGo7VYlKrSQaX6nzJGZb7QrSDfDsMUE53A"
TELEGRAM_CHAT_ID = "7568661553"

# قائمة وكالات المستخدمين
USER_AGENTS = [
    "Instagram 219.0.0.12.117 Android (30/11; 420dpi; 1080x2340; samsung; SM-A715F; a71; qcom; en_US)",
    "Instagram 200.1.0.29.121 Android (29/10; 480dpi; 1080x1920; google; Pixel 2; walleye; qcom; en_US)",
    "Instagram 250.0.0.17.113 Android (31/12; 420dpi; 1080x2340; OnePlus; GM1913; OnePlus7Pro; qcom; en_US)"
]

# إعدادات السيرفر الخاص بالبوت
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت شغال 24 ساعة!"

def run():
    app.run(host='0.0.0.0', port=8080)

# تشغيل السيرفر في الخلفية
Thread(target=run).start()

# توليد اسم مستخدم عشوائي
def generate_username(length=4):
    chars = string.ascii_lowercase + string.digits + "._"
    while True:
        username = ''.join(random.choices(chars, k=length))
        if username[0] not in "._" and username[-1] not in "._":
            return username

# إرسال رسالة إلى تيليجرام
async def send_to_telegram(message):
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            await session.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as e:
        print(f"[!] خطأ في تيليجرام: {e}")

# التحقق من توفر اسم المستخدم
async def check_username(username):
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = "https://i.instagram.com/api/v1/users/check_username/"
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "X-IG-App-ID": "567067343352427",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }

            async with session.post(url, headers=headers, data={"username": username}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("available"):
                        print(f"[✓] متاح: {username}")
                        with open("available.txt", "a") as f:
                            f.write(username + "\n")
                        await send_to_telegram(f"اسم المستخدم المتاح: {username}")
                    else:
                        print(f"[X] غير متاح: {username}")
                elif resp.status == 429:
                    print(f"[!] تم تحديد المعدل - الانتظار لمدة 30 ثانية")
                    await asyncio.sleep(30)  # الانتظار لمدة 30 ثانية إذا كان هناك حد للمعدل
                else:
                    print(f"[!] {username} - HTTP {resp.status}")
    except Exception as e:
        print(f"[!] خطأ في التحقق من {username}: {e}")
    return False  # إرجاع False إذا حدث خطأ

# الحلقة الرئيسية
async def main():
    while True:
        username = generate_username()  # توليد اسم مستخدم عشوائي
        await check_username(username)  # التحقق من توفر اسم المستخدم
        # إضافة تأخير عشوائي بين 1 و 3 ثواني بين كل محاولة
        await asyncio.sleep(random.randint(1, 3))

# تشغيل كل شيء
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())  # تشغيل الحلقة الرئيسية بشكل مستمر دون توقف
    except KeyboardInterrupt:
        print("تم إيقاف التنفيذ.")
