from copy import deepcopy

from database import DatabaseConnector
from datetime import datetime
from telebot import types
import telebot
import inspect

token = ''
bot = telebot.TeleBot(token)
db = DatabaseConnector()
data = {}


def write(message, response):
    bot.send_message(message.from_user.id, response)


@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    if message.text == '/start':
        write(message, 'Доступны следующие команды:\n'
                       '/add\n'
                       '/delete\n'
                       '/list\n'
                       '/find\n'
                       '/borrow\n'
                       '/retrieve\n'
                       '/stats\n'
              )
    elif message.text == '/list':
        ans = db.list_books()
        if ans != ';':
            write(message, ans)
        else:
            write(message, 'Нет книг')
    elif message.text == '/retrieve':
        ans = db.retrieve({'user_id': message.from_user.id, 'date_point': datetime.now()})
        if not ans:
            write(message, 'Нечего возвращать')
        else:
            write(message, f"Вы вернули книгу {ans[0]} {ans[1]} {ans[2]}")
    elif message.text in ['/add', '/delete', '/borrow', '/stats', '/find']:
        handle_start(message)
    else:
        write(message, 'Введенное не является командой')


def handle_start(message):
    global data
    data.update({'type': message.text})
    write(message, 'Введите название книги:')
    bot.register_next_step_handler(message, handle_title)


def handle_title(message):
    global data
    data.update({inspect.currentframe().f_code.co_name[7:]: message.text})
    write(message, 'Введите автора:')
    bot.register_next_step_handler(message, handle_author)


def handle_author(message):
    global data
    data.update({inspect.currentframe().f_code.co_name[7:]: message.text})
    write(message, 'Введите год издания:')
    bot.register_next_step_handler(message, handle_published)


def handle_published(message):
    global data
    try:
        data.update({inspect.currentframe().f_code.co_name[7:]: int(message.text)})
    except:
        write(message, 'Напиши число')
        bot.register_next_step_handler(message, handle_published)
    else:
        handle_end(message)


def handle_end(message):
    global data
    type = data.pop('type')
    data.update({'date_point': datetime.now()})

    if type == '/add':
        id = db.add_book(deepcopy(data))
        write(message, f"Книга добавлена ({id})" if id else "Ошибка при добавлении книги")

    elif type == '/delete':

        if db.get_book(deepcopy(data)):
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='yes_delete'))
            keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='no_delete'))
            bot.send_message(message.from_user.id,
                             text=f"Найдена книга: {data['title']} {data['author']} {data['published']}. Удаляем?",
                             reply_markup=keyboard)
        else:
            write(message, 'Нет такой книги')

    elif type == '/find':

        ans = db.get_book(deepcopy(data))
        write(message, f"Найдена книга: {data['title']} {data['author']} {data['published']}" if ans else 'Такой книги у нас нет')

    elif type == '/borrow':

        if db.get_book(deepcopy(data)):
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='yes_borrow'))
            keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='no_borrow'))
            bot.send_message(message.from_user.id,
                             text=f"Найдена книга: {data['title']} {data['author']} {data['published']}. Берем?",
                             reply_markup=keyboard)
        else:
            write(message, 'Нет такой книги')

    elif type == '/stats':

        ans = db.find_stat(deepcopy(data))
        if not ans:
            write(message, 'Нет такой книги')
        else:
            write(message, f"Статистика доступна по адресу http://127.0.0.1:8080/download/{ans}/")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global data
    if call.data == 'yes_delete':
        ans = db.delete(deepcopy(data))
        bot.send_message(call.message.chat.id, 'Книга удалена' if ans else 'Невозможно удалить книгу')

    elif call.data == 'yes_borrow':
        ans = db.borrow(deepcopy(data | {'user_id': call.message.chat.id}))
        bot.send_message(call.message.chat.id, 'Вы взяли книгу' if ans else 'Книгу сейчас невозможно взять')
