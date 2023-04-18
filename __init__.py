from telegram import *
from app import *
import threading

class TelegramThread(threading.Thread):
    def run(self):
        bot.infinity_polling()

class FlaskThread(threading.Thread):
    def run(self):
        app.run('0.0.0.0', port=8080)

if __name__ == '__main__':
    tt = TelegramThread()
    ft = FlaskThread()
    tt.start()
    ft.start()
