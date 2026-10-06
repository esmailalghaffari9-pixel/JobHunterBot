import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters
)
from google import genai
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# إعداد السجلات لمتابعة الأخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# قراءة المفاتيح من بيئة العمل (Render variables)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تهيئة عميل Gemini الجديد
client = genai.Client(api_key=GEMINI_API_KEY)

# دالة للرد على الرسائل عبر Gemini
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        # استخدام نموذج gemini-2.5-flash للرد السريع
        response = client.models.generate_content(
            model='gemini-1.5-flash',

            contents=user_text
        )
        await update.message.reply_text(response.text)
except Exception as e:
    print("MY_ERROR:", str(e))
    logging.error(f"Error: {e}")
    await update.message.reply_text("عذراً، حدث خطأ أثناء معالجة طلبك.")

            print("MY_ERROR:", str(e))
    logging.error(f"Error: {e}")

        await update.message.reply_text("عذراً، حدث خطأ أثناء معالجة طلبك.")

# خادم وهمي لإبقاء بوت Render نشطاً (Web Service Dummy Server)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

def main():
    # تشغيل الخادم الوهمي في خيط منفصل
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # بناء وتشغيل بوت تيليجرام
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is polling...")
    app.run_polling()

if __name__ == '__main__':
    main()
