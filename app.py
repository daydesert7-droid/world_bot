import threading
from flask import Flask
from bot import main as bot_main

app = Flask(__name__)

def start_bot():
    bot_main()

@app.route('/')
def home():
    return "Telegram Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)