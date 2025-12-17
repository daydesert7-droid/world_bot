import threading
import time
import logging
import sys
import os
from flask import Flask

# Настройка логгера Flask
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Глобальная переменная для хранения потока бота
bot_thread = None
bot_running = False
bot_process = None

def start_bot():
    """Запуск Telegram бота в отдельном потоке"""
    global bot_running
    
    try:
        # Добавляем текущую директорию в путь Python
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from bot import run_bot
        
        bot_running = True
        logger.info("Запуск Telegram бота...")
        
        # Запускаем бота
        run_bot()
        
    except ImportError as e:
        logger.error(f"Ошибка импорта модуля bot: {e}")
        bot_running = False
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
        bot_running = False

@app.route('/')
def home():
    """Главная страница"""
    status = "работает" if bot_running else "остановлен"
    return f"""
    <html>
        <head>
            <title>Telegram Bot Status</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: white;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 40px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                }}
                .status {{ 
                    display: inline-block;
                    padding: 10px 20px;
                    border-radius: 50px;
                    font-weight: bold;
                    margin: 10px 0;
                }}
                .running {{ 
                    background-color: #10b981;
                    color: white;
                }}
                .stopped {{ 
                    background-color: #ef4444;
                    color: white;
                }}
                h1 {{
                    margin-top: 0;
                    font-size: 2.5rem;
                }}
                .btn {{
                    display: inline-block;
                    background: white;
                    color: #667eea;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 50px;
                    margin: 10px 5px;
                    font-weight: bold;
                    transition: all 0.3s;
                }}
                .btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid rgba(255, 255, 255, 0.2);
                    text-align: center;
                    font-size: 0.9rem;
                    opacity: 0.8;
                }}
                .log-container {{
                    background: rgba(0, 0, 0, 0.2);
                    border-radius: 10px;
                    padding: 15px;
                    margin-top: 20px;
                    max-height: 200px;
                    overflow-y: auto;
                    font-family: monospace;
                    font-size: 0.9rem;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Telegram Bot Status</h1>
                <p>Статус бота: <span class="status {'running' if bot_running else 'stopped'}">{status}</span></p>
                
                <div>
                    <a href="/start" class="btn">🔄 Перезапустить бота</a>
                    <a href="/health" class="btn">❤️ Проверить здоровье</a>
                    <a href="/logs" class="btn">📊 Показать логи</a>
                </div>
                
                <div class="log-container">
                    <strong>Последние действия:</strong><br>
                    • Бот {'работает нормально' if bot_running else 'не запущен'}<br>
                    • Сервер активен<br>
                    • Время сервера: {time.strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                
                <div class="footer">
                    <p>Развернуто на Render.com • Python 3.13.4 • Работает 24/7</p>
                    <p>Telegram Bot API: python-telegram-bot v21.7</p>
                </div>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """Эндпоинт для проверки здоровья"""
    if bot_running:
        return {
            "status": "healthy",
            "bot_running": True,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }, 200
    else:
        return {
            "status": "unhealthy",
            "bot_running": False,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }, 500

@app.route('/start')
def start_bot_endpoint():
    """Ручной запуск/перезапуск бота"""
    global bot_thread, bot_running
    
    try:
        # Если бот уже запущен, сначала останавливаем
        if bot_thread and bot_thread.is_alive():
            bot_running = False
            logger.info("Остановка текущего бота...")
            time.sleep(2)
        
        # Запускаем новый поток с ботом
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        
        # Даем время на инициализацию
        time.sleep(3)
        
        if bot_running:
            logger.info("Бот успешно запущен")
            return {
                "status": "success",
                "message": "Бот успешно запущен",
                "bot_running": True
            }, 200
        else:
            return {
                "status": "error",
                "message": "Не удалось запустить бота",
                "bot_running": False
            }, 500
            
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "bot_running": False
        }, 500

@app.route('/logs')
def show_logs():
    """Показать последние логи"""
    try:
        log_content = "Логи не найдены"
        log_file = 'logs/bot_main.log'
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                # Читаем последние 50 строк
                lines = f.readlines()[-50:]
                log_content = "".join(lines)
        
        return f"""
        <html>
            <head>
                <title>Bot Logs</title>
                <style>
                    body {{ font-family: monospace; margin: 20px; background: #f5f5f5; }}
                    .logs {{ background: white; padding: 20px; border-radius: 5px; }}
                    pre {{ white-space: pre-wrap; word-wrap: break-word; }}
                </style>
            </head>
            <body>
                <h2>📋 Последние логи бота</h2>
                <div class="logs">
                    <pre>{log_content}</pre>
                </div>
                <br>
                <a href="/">← Назад</a>
            </body>
        </html>
        """
    except Exception as e:
        return f"Ошибка при чтении логов: {str(e)}", 500

@app.route('/stop')
def stop_bot():
    """Остановка бота (для администрирования)"""
    global bot_running
    
    bot_running = False
    logger.info("Команда на остановку бота получена")
    
    return {
        "status": "success",
        "message": "Команда на остановку бота отправлена",
        "bot_running": False
    }, 200

def keep_alive():
    """Функция для поддержания активности (пустая, так как Flask уже слушает порт)"""
    pass

# Запускаем бота при старте приложения
if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Даем время на инициализацию бота
    time.sleep(5)
    
    # Запускаем Flask сервер
    logger.info("Запуск Flask сервера...")
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False,
        use_reloader=False  # Отключаем reloader, так как он создает дополнительные процессы
    )