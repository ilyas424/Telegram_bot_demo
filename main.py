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
    except IndexError:
        pass


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
    except IndexError:
        pass


def vote_i_play(callback):
    bot.answer_callback_query(callback.id)
    # bot.send_message(callback.message.chat.id, callback.data)

    # сразу формируем список игроков в формате:
    # [{'id':<id>, 'name': <name},...]
    # будем в этот список сперва считывать данные, затем его дополнять и
    # на его основе формировать новое содержимое файла

    players_list = []

    try:
        with open('data/players.csv', encoding='utf-8', mode="r", newline='') as csvfile:
            reader = csv.reader(csvfile)
            players_list = [{'id': i[0], 'name': i[1]} for i in reader]
            for el in players_list:
                if int(el['id']) == callback.from_user.id:
                    # если мы уже в списке, то вызываем return, чтобы дальше не исполнять код!
                    # и тогда дальше можно обойтись без лишних if-ов и т.д.
                    return bot.send_message(
                        callback.message.chat.id,
                        f"{callback.from_user.first_name}, ты уже есть в списке"
                    )
    except FileNotFoundError:
        pass
    except IndexError:
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

    players_list = []

    try:
        with open('data/players.csv', encoding='utf-8', mode="r", newline='') as csvfile:
            reader = csv.reader(csvfile)
            players_list = [{'id': i[0], 'name': i[1]} for i in reader]

            if {'id': str(callback.from_user.id), 'name': callback.from_user.first_name} not in players_list:
                # если мы уже в списке, то вызываем return, чтобы дальше не исполнять код!
                # и тогда дальше можно обойтись без лишних if-ов и т.д.
                return bot.send_message(
                    callback.message.chat.id,
                    f"{callback.from_user.first_name}, тебя нет в списке"
                )
    except FileNotFoundError:
        pass
    except IndexError:
        pass

    players_list.remove({
        'id': str(callback.from_user.id),
        'name': callback.from_user.first_name
    })

    with open('data/players.csv', 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for player in players_list:
            writer.writerow([player['id'], player['name']])
        bot.send_message(callback.message.chat.id, f"{callback.from_user.first_name}, удален из списка")


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
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("Изменить фото")
    btn2 = types.KeyboardButton("Изменить текст")
    btn3 = types.KeyboardButton("Отмена")
    markup.add(btn1, btn2, btn3)
    bot.send_message(callback.message.chat.id, text='Что изменить?', reply_markup=markup)


def edit_description(message):
    if message.from_user.id in settings.ADMINS_LIST:
        try:
            if message.text != '':
                with open('data/location.txt', 'w', encoding='utf-8') as file:
                    file.write(message.text)
                bot.send_message(message.chat.id, 'Сохранил текст')
            else:
                bot.send_message(message.chat.id, text=f'данные некорректны')
        except:
            bot.send_message(message.chat.id, 'Что-то пошло не так, процесс прерван')
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так, процесс прерван')


def edit_photo(message):
    if message.from_user.id in settings.ADMINS_LIST:
        try:
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open('data/image.jpg', 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(message.chat.id, 'Сохранил фото')
        except:
            bot.send_message(message.chat.id, 'Что-то пошло не так, процесс прерван')
    else:
        bot.send_message(message.chat.id, 'Процесс прерван')


def back(callback):
    bot.answer_callback_query(callback.id)
    bot.edit_message_reply_markup(callback.message.chat.id, callback.message.id,
                                  reply_markup=get_admin_commands_keyboard())


def remove_player(callback):
    bot.answer_callback_query(callback.id)

    try:
        with open('data/players.csv', encoding='utf-8') as cvsfile:
            reader = csv.reader(cvsfile)
            spisok = [' '.join(map(str, i)) for i in reader]
            players_list = [f'{spisok[i]}' for i in range(len(spisok))]
            if spisok == []:
                return bot.send_message(callback.message.chat.id, f"Список пуст")
            else:
                bot.edit_message_reply_markup(callback.message.chat.id, callback.message.id,
                                              reply_markup=get_players(players_list))
    except FileNotFoundError:
        pass


def refresh_players_list(callback):
    bot.answer_callback_query(callback.id)

    with open('data/players.csv', encoding='utf-8', mode="w") as csvfile:
        csv.reader(csvfile)
        bot.send_message(callback.message.chat.id, 'Список обновлен')


admin_commands_with_handlers = OrderedDict()
admin_commands_with_handlers["Изменить инф-цию о следующей игре"] = change_next_game_info
admin_commands_with_handlers["Удалить игрока"] = remove_player
admin_commands_with_handlers["Обновить список"] = refresh_players_list

edit_info_commands_with_handlers = OrderedDict()
edit_info_commands_with_handlers["<-- назад"] = back


def get_admin_commands_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for command in admin_commands_with_handlers:
        keyboard.add(types.InlineKeyboardButton(text=command, callback_data=command))
    return keyboard


def players_list_command_delete(callback):
    bot.answer_callback_query(callback.id)

    data = callback.data.split()
    players_list = []

    try:
        with open('data/players.csv', encoding='utf-8', mode="r") as csvfile:
            reader = csv.reader(csvfile)
            players_list = [{'id': i[0], 'name': i[1]} for i in reader]

            if {'id': data[0], 'name': data[1]} not in players_list:
                # если мы уже в списке, то вызываем return, чтобы дальше не исполнять код!
                # и тогда дальше можно обойтись без лишних if-ов и т.д.
                return bot.send_message(
                    callback.message.chat.id,
                    f"{callback.from_user.first_name}, скорее всего список устарел"
                )
    except FileNotFoundError:
        pass

    try:
        players_list.remove({
            'id': data[0],
            'name': data[1]
        })

        with open('data/players.csv', 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for player in players_list:
                writer.writerow([player['id'], player['name']])
            bot.send_message(callback.message.chat.id, f"{data[1]}, удален из списка")
    except ValueError:
        pass


def get_players(players: list):
    keyboard = types.InlineKeyboardMarkup()
    for command in players:
        keyboard.add(types.InlineKeyboardButton(text=command, callback_data=command))
    keyboard.add(types.InlineKeyboardButton(text='<-- назад', callback_data='<-- назад'))
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
    logger.info(f"Callback command '{callback.data}' from User {callback.from_user.id}")
    if callback.data in common_commands_with_handlers:
        common_commands_with_handlers[callback.data](callback)
    elif callback.data == 'Изменить инф-цию о следующей игре' and callback.from_user.id in settings.ADMINS_LIST:
        change_next_game_info(callback)
    elif callback.data in admin_commands_with_handlers and callback.from_user.id in settings.ADMINS_LIST:
        admin_commands_with_handlers[callback.data](callback)
    elif callback.data in edit_info_commands_with_handlers and callback.from_user.id in settings.ADMINS_LIST:
        edit_info_commands_with_handlers[callback.data](callback)
    elif callback.from_user.id in settings.ADMINS_LIST:
        players_list_command_delete(callback)
    else:
        bot.send_message(callback.message.chat.id,
                         f'{callback.from_user.first_name}, недостаточно прав для выполнения операции')


@bot.message_handler(content_types=['text', 'photo'])
def text_message_handler(message):
    logger.info(f"Text command '{message.text}' from User {message.from_user.id}")
    remove = telebot.types.ReplyKeyboardRemove()
    if message.text == '@football_tatarlar_Bot':
        open_common_commands(message)
    elif message.text == 'Изменить фото' and message.from_user.id in settings.ADMINS_LIST:
        bot.send_message(message.chat.id, text='Отправьте новое фото', reply_markup=remove)
        bot.register_next_step_handler(message, edit_photo)
    elif message.text == "Изменить текст" and message.from_user.id in settings.ADMINS_LIST:
        bot.send_message(message.chat.id, text='Введите новую информацию', reply_markup=remove)
        bot.register_next_step_handler(message, edit_description)
    elif message.text == "Отмена" and message.from_user.id in settings.ADMINS_LIST:
        bot.send_message(message.chat.id, text='Убрал', reply_markup=remove)
    else:
        pass


if __name__ == '__main__':
    bot.infinity_polling(timeout=10, long_polling_timeout = 5)
