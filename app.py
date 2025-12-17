import threading
import time
import logging
from flask import Flask

# Настройка логгера Flask
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Глобальная переменная для хранения потока бота
bot_thread = None
bot_running = False

def start_bot():
    """Запуск Telegram бота в отдельном потоке"""
    global bot_running
    try:
        from bot import run_bot
        
        bot_running = True
        logger.info("Запуск Telegram бота...")
        run_bot()
    except ImportError as e:
        logger.error(f"Ошибка импорта модуля bot: {e}")
        bot_running = False
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        bot_running = False

@app.route('/')
def home():
    """Главная страница"""
    status = "работает" if bot_running else "остановлен"
    return f"""
    <html>
        <head>
            <title>Telegram Bot Status</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .status {{ padding: 10px; border-radius: 5px; }}
                .running {{ background-color: #d4edda; color: #155724; }}
                .stopped {{ background-color: #f8d7da; color: #721c24; }}
                a {{ color: #007bff; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>🤖 Telegram Bot Status</h1>
            <p>Бот <span class="status {'running' if bot_running else 'stopped'}">{status}</span></p>
            <p><a href="/health">Проверить работоспособность</a></p>
            <p><a href="/start">Перезапустить бота</a></p>
            <hr>
            <p><small>Развернуто на Render.com • 24/7 работа</small></p>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """Эндпоинт для проверки здоровья"""
    if bot_running:
        return "OK", 200
    else:
        return "Bot is not running", 500

@app.route('/start')
def start_bot_endpoint():
    """Ручной запуск/перезапуск бота"""
    global bot_thread, bot_running
    
    if bot_thread and bot_thread.is_alive():
        return "Бот уже запущен", 200
    
    try:
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        time.sleep(2)  # Даем время на инициализацию
        
        if bot_running:
            return "Бот успешно запущен", 200
        else:
            return "Не удалось запустить бота", 500
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        return f"Ошибка: {str(e)}", 500

@app.route('/stop')
def stop_bot():
    """Остановка бота (для администрирования)"""
    global bot_running
    
    # В реальности нужно аккуратно останавливать бота
    # Здесь просто меняем флаг
    bot_running = False
    return "Команда на остановку бота отправлена", 200

def keep_alive():
    """Функция для поддержания активности (пустая, так как Flask уже слушает порт)"""
    pass

# Запускаем бота при старте приложения
if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Даем время на инициализацию бота
    time.sleep(3)
    
    # Запускаем Flask сервер
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False  # Отключаем reloader, так как он создает дополнительные процессы
    )