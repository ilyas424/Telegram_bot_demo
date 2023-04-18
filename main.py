import sys
import csv
from collections import OrderedDict

from loguru import logger
import telebot
from telebot import types

import settings


bot = telebot.TeleBot(settings.TOKEN)
logger.add("bot.log", format="[{time}] {level}: {message}", level="INFO", backtrace=True, diagnose=True)
logger.configure()


def get_next_game_info(callback):
    bot.answer_callback_query(callback.id)
    try:
        with open('data/location.txt', encoding='utf-8') as file:
            content = file.read()
            if content != '':
                bot.send_message(callback.message.chat.id, content)
                with open('data/image.jpg', 'rb') as photo:
                    bot.send_photo(callback.message.chat.id, photo)
            else:
                bot.send_message(callback.message.chat.id, 'Информации нет!')
    except FileNotFoundError:
        bot.send_message(callback.message.chat.id, 'Информации нет!')


def get_players_list_for_next_game(callback):
    bot.answer_callback_query(callback.id)
    try:
        with open('data/players.csv', encoding='utf-8') as cvsfile:
            reader = csv.reader(cvsfile)
            spisok = [' '.join(map(str, i)) for i in reader]
            players_list = [f'{i + 1}) {spisok[i]}' for i in range(len(spisok))]
            if spisok == []:
                bot.send_message(callback.message.chat.id, f"Состав на ближайшую игру:\n-")
            else:
                players_list = '\n'.join(players_list)
                bot.send_message(callback.message.chat.id, f"Состав на ближайшую игру:\n{players_list}")
    except FileNotFoundError:
        bot.send_message(callback.message.chat.id, 'Состав на ближайшую игру:\n-')


def vote_i_play(callback):
    bot.answer_callback_query(callback.id)
    # bot.send_message(callback.message.chat.id, callback.data)

    # сразу формируем список игроков в формате:
    # [{'id':<id>, 'name': <name},...]
    # будем в этот список сперва считывать данные, затем его дополнять и
    # на его основе формировать новое содержимое файла

    players_list = []

    try:
        with open('data/players.csv', encoding='utf-8', mode="r") as csvfile:
            reader = csv.reader(csvfile)
            players_list = [{'id': i[0], 'name': i[1]} for i in reader]
            if callback.from_user.id in players_list:
                # если мы уже в списке, то вызываем return, чтобы дальше не исполнять код!
                # и тогда дальше можно обойтись без лишних if-ов и т.д.
                return bot.send_message(
                    callback.message.chat.id,
                    f"{callback.from_user.first_name}, ты уже есть в списке"
                )
    except FileNotFoundError:
        pass

    players_list.append({
        'id': callback.from_user.id,
        'name': callback.from_user.first_name
    })

    with open('data/players.csv', 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for player in players_list:
            writer.writerow([player['id'], player['name']])
        bot.send_message(callback.message.chat.id, f"{callback.from_user.first_name}, добавлен в список")


def vote_i_dont_play(callback):
    bot.answer_callback_query(callback.id)
    bot.send_message(callback.message.chat.id, callback.data)

# Ключ словаря - текстовая команда, занчение по ключу - функция обработчий этой команды
common_commands_with_handlers = OrderedDict()
common_commands_with_handlers["Информация о ближайшей игре"] = get_next_game_info
common_commands_with_handlers["Состав на ближайшую игру"] = get_players_list_for_next_game
common_commands_with_handlers["Я играю"] = vote_i_play
common_commands_with_handlers["Я не играю"] = vote_i_dont_play

def get_common_commands_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for command in common_commands_with_handlers:
        keyboard.add(types.InlineKeyboardButton(text=command, callback_data=command))
    return keyboard


def change_next_game_info(callback):
    bot.answer_callback_query(callback.id)
    bot.send_message(callback.message.chat.id, callback.data)

def remove_player(callback):
    bot.answer_callback_query(callback.id)
    bot.send_message(callback.message.chat.id, callback.data)

def refresh_players_list(callback):
    bot.answer_callback_query(callback.id)
    bot.send_message(callback.message.chat.id, callback.data)

admin_commands_with_handlers = OrderedDict()
admin_commands_with_handlers["Изменить инф-цию о следующей игре"] = change_next_game_info
admin_commands_with_handlers["Удалить игрока"] = remove_player
admin_commands_with_handlers["Обновить список"] = refresh_players_list

def get_admin_commands_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for command in admin_commands_with_handlers:
        keyboard.add(types.InlineKeyboardButton(text=command, callback_data=command))
    return keyboard



@bot.message_handler(commands=['start'])
def open_common_commands(message):
    logger.info(f"User {message.from_user.id} asks for commands")
    bot.send_message(message.chat.id, 'Выберите команду', reply_markup=get_common_commands_keyboard())


# @bot.message_handler(content_types=['text', 'photo'])
@bot.message_handler(commands=['admin'])
def open_admin_commands(message):
    if message.from_user.id in settings.ADMINS_LIST:
        logger.info(f"User {message.from_user.id} asks for admin commands")
        return bot.send_message(message.chat.id, 'Выберите команду', reply_markup=get_admin_commands_keyboard())
    logger.warning(f"User {message.from_user.id} tried to get admin commands without permissions!")
    bot.send_message(message.chat.id, text='Недостаточно прав')


@bot.callback_query_handler(func=lambda message: True)
def process_callback(callback):
    logger.info(f"Callback command '{callback.data}' from User {callback.message.from_user.id}")
    if callback.data in common_commands_with_handlers:
        common_commands_with_handlers[callback.data](callback)
    elif callback.data in admin_commands_with_handlers:
        admin_commands_with_handlers[callback.data](callback)


@bot.message_handler(content_types=['text', 'photo'])
def text_message_handler(message):
    logger.info(f"Text command '{message.text}' from User {message.from_user.id}")
    if message.text == '@football_tatarlar_Bot':
        open_common_commands(message)
    else:
        bot.send_message(message.chat.id, 'Неизвестная команда')

#     if message.text == 'Изменить информацию о следующей игре' and message.from_user.id  in settings.ADMINS_LIST:
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
#         btn1 = types.KeyboardButton("Изменить фото")
#         btn2 = types.KeyboardButton("Изменить текст")
#         btn3 = types.KeyboardButton("Отмена")
#         markup.add(btn1, btn2, btn3)
#         bot.send_message(message.chat.id, text='Что изменить?', reply_markup=markup)
#         bot.register_next_step_handler(message, edit_info)

#     if message.text == 'Удалить игрока' and message.from_user.id  in settings.ADMINS_LIST:
#         with open('data/players.csv', encoding='utf-8') as cvsfile:
#             reader = csv.reader(cvsfile)
#             spisok = [' '.join(map(str, i)) for i in reader]
#             spisok_ref = [f'{i + 1}) {spisok[i]}' for i in range(len(spisok))]
#             if spisok == []:
#                 bot.send_message(message.chat.id, f"Список пуст")
#             else:
#                 spisok_req = '\n'.join(map(str, spisok_ref))
#                 bot.send_message(message.chat.id, f"""{spisok_req}""")
#                 bot.send_message(message.chat.id, text='введите номер игрока')
#                 bot.register_next_step_handler(message, edit_list_players)

#     if message.text == 'Обновить список' and message.from_user.id  in settings.ADMINS_LIST:
#         with open('data/players.csv', 'w', encoding='utf-8') as cvsfile:
#             csv.reader(cvsfile)
#         bot.send_message(message.chat.id, "Список обновлен")

#     if message.text == 'Скрыть админку' and message.from_user.id  in settings.ADMINS_LIST:
#         remove = telebot.types.ReplyKeyboardRemove()
#         bot.send_message(message.chat.id, 'Скрыл', reply_markup=remove)


# def edit_info(message):
#     remove = telebot.types.ReplyKeyboardRemove()
#     if message.text == 'Изменить текст':
#         bot.send_message(message.chat.id, text='Введите новую информацию',reply_markup=remove)
#         bot.register_next_step_handler(message, edit_text)
#     elif message.text == 'Изменить фото':
#         bot.send_message(message.chat.id, text='Отправте новое фото', reply_markup=remove)
#         bot.register_next_step_handler(message, edit_photo)
        
#     elif message.text == 'Отмена':
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
#         btn1 = types.KeyboardButton("Изменить информацию о следующей игре")
#         btn2 = types.KeyboardButton("Удалить игрока")
#         btn3 = types.KeyboardButton("Обновить список")
#         btn4 = types.KeyboardButton("Скрыть админку")
#         markup.add(btn1, btn2, btn3, btn4)
#         bot.send_message(message.chat.id, text='Вернул вас в главное меню', reply_markup=markup)


# def edit_text(message):
#     if message.text != '':
#         with open('data/location.txt', 'w', encoding='utf-8') as file:
#             file.write(message.text)
#         bot.send_message(message.chat.id, 'Сохранил текст')
#     else:
#         bot.send_message(message.chat.id, text=f'данные некорректны')


# def edit_photo(message):
#     file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
#     downloaded_file = bot.download_file(file_info.file_path)
#     with open('data/image.jpg', 'wb') as new_file:
#         new_file.write(downloaded_file)
#     bot.send_message(message.chat.id, 'Сохранил фото')


# def edit_list_players(message):
#     with open('data/players.csv', encoding='utf-8') as cvsfile:
#         reader = csv.reader(cvsfile)
#         spisok_def = [i for i in reader]
#     if message.text != '' and message.text.isdigit() and (
#             int(message.text) <= len(spisok_def) and int(message.text) > 0):
#         spisok_def.pop(int(message.text) - 1)

#         with open('data/players.csv', 'w', encoding='utf-8', newline='') as cvsfile:
#             writer = csv.writer(cvsfile)
#             for line in spisok_def:
#                 writer.writerow(line)
#             bot.send_message(
#                 message.chat.id,
#                 f"Великий админ, удалил игрока под номером {message.text}")
#     else:
#         bot.send_message(message.chat.id, text=f'Ввод некорректен')


# @bot.callback_query_handler(func=lambda message: True)
# def ans(message):
#     chat_id = message.message.chat.id

#     elif message.data == "Я не играю":
#         bot.answer_callback_query(message.id)
#         with open('data/players.csv', encoding='utf-8') as cvsfile:
#             reader = csv.reader(cvsfile)
#             spisok = [i for i in reader]
#         if [str(message.from_user.id)[:4] + ' ' + message.from_user.first_name
#             ] not in spisok:
#             bot.send_message(chat_id,
#                              f"{message.from_user.first_name}, тебя нет в списке")
#         else:
#             spisok = [
#                 i for i in spisok if i !=
#                                      [str(message.from_user.id)[:4] + ' ' + message.from_user.first_name]
#             ]
#             with open('data/players.csv', 'w', encoding='utf-8', newline='') as cvsfile:
#                 writer = csv.writer(cvsfile)
#                 for line in spisok:
#                     writer.writerow(line)
#                 bot.send_message(
#                     chat_id,
#                     f"{message.from_user.first_name}, удалил тебя из списка")


#     elif message.data == "Я играю":
#         bot.answer_callback_query(message.id)
#         with open('data/players.csv', encoding='utf-8', mode="a") as csvfile:
#             reader = csv.reader(csvfile)
#             spisok = [i for i in reader]
#         if [str(message.from_user.id)[:4] + ' ' + message.from_user.first_name
#             ] in spisok:
#             bot.send_message(
#                 chat_id,
#                 f"{message.from_user.first_name}, ты уже есть в списке")
#         else:
#             with open('data/players.csv', 'a+', encoding='utf-8',
#                       newline='') as csvfile:
#                 write = csv.writer(csvfile)
#                 write.writerow(
#                     [str(message.from_user.id)[:4] + ' ' + message.from_user.first_name])
#                 bot.send_message(chat_id,
#                                  f"""{message.from_user.first_name}, записал тебя.
# (Если у тебя не получается, то не забудь нажать кнопку "Я не играю "🙄)
#           """)


if __name__ == '__main__':
    bot.polling(non_stop=True, interval=0)
