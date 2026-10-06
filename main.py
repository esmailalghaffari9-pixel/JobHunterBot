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

# إعداد السجلات لمتابعة الأخطاء #
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# قراءة المفاتيح من بيئة العمل #
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# تهيئة Gemini #
client = genai.Client(api_key=GEMINI_API_KEY)

# دالة للرد على الرسائل عبر Gemini #
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    user_text = update.message.text
    try:
        # استخدام النموذج المستقر المدعوم #
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_text
        )
        
        # التأكد من وجود نص في الرد قبل إرساله #
        if response and response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("عذراً، لم أتمكن من توليد إجابة مناسبة.")
            
    except Exception as e:
        print("MY_ERROR:", str(e))
        logging.error(f"Error: {e}")
        await update.message.reply_text("عذراً، حدث خطأ أثناء معالجة طلبك.")

# خادم وهمي لإبقاء بوت الاستضافة نشطاً #
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
    # تشغيل الخادم الوهمي في خيط منفصل #
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # بناء وتشغيل بوت تيليجرام #
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is polling...")
    app.run_polling()

if __name__ == '__main__':
    main()
