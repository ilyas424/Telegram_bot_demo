import telebot
from telebot import types
import csv

import settings

bot = telebot.TeleBot(settings.TOKEN)


@bot.message_handler(commands=['start'])
def send_anytext(message):
    print(message.from_user.id)
    chat_id = message.chat.id
    text = 'Выберите команду'
    bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=list_commands(chat_id))


@bot.message_handler(commands=['admin'])
def is_admin(message):
    if message.from_user.id in settings.list_admin:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("Изменить информацию о следующей игре")
        btn2 = types.KeyboardButton("Удалить игрока")
        btn3 = types.KeyboardButton("Обновить список")
        btn4 = types.KeyboardButton("Скрыть админку")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, text='Приветствую тебя великий админ', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text='Недостаточно прав доступа')


@bot.message_handler(content_types=['text', 'photo'])
def send_call(message):
    chat_id = message.chat.id
    if message.text == '@football_tatarlar_Bot':
        text = 'Выберите команду'
        bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=list_commands(chat_id))

    if message.text == 'Изменить информацию о следующей игре' and message.from_user.id  in settings.list_admin:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("Изменить фото")
        btn2 = types.KeyboardButton("Изменить текст")
        btn3 = types.KeyboardButton("Отмена")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, text='Что изменить?', reply_markup=markup)
        bot.register_next_step_handler(message, edit_info)

    if message.text == 'Удалить игрока' and message.from_user.id  in settings.list_admin:
        with open('data/players.csv', encoding='utf-8') as cvsfile:
            reader = csv.reader(cvsfile)
            spisok = [' '.join(map(str, i)) for i in reader]
            spisok_ref = [f'{i + 1}) {spisok[i]}' for i in range(len(spisok))]
            if spisok == []:
                bot.send_message(message.chat.id, f"Список пуст")
            else:
                spisok_req = '\n'.join(map(str, spisok_ref))
                bot.send_message(message.chat.id, f"""{spisok_req}
""")
                bot.send_message(message.chat.id, text='введите номер игрока')
                bot.register_next_step_handler(message, edit_list_players)

    if message.text == 'Обновить список' and message.from_user.id  in settings.list_admin:
        with open('data/players.csv', 'w', encoding='utf-8') as cvsfile:
            csv.reader(cvsfile)
        bot.send_message(message.chat.id, "Список обновлен")

    if message.text == 'Скрыть админку' and message.from_user.id  in settings.list_admin:
        remove = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Скрыл', reply_markup=remove)


def edit_info(message):
    remove = telebot.types.ReplyKeyboardRemove()
    if message.text == 'Изменить текст':
        bot.send_message(message.chat.id, text='Введите новую информацию',reply_markup=remove)
        bot.register_next_step_handler(message, edit_text)
    elif message.text == 'Изменить фото':
        bot.send_message(message.chat.id, text='Отправте новое фото', reply_markup=remove)
        bot.register_next_step_handler(message, edit_photo)
        
    elif message.text == 'Отмена':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("Изменить информацию о следующей игре")
        btn2 = types.KeyboardButton("Удалить игрока")
        btn3 = types.KeyboardButton("Обновить список")
        btn4 = types.KeyboardButton("Скрыть админку")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, text='Вернул вас в главное меню', reply_markup=markup)


def edit_text(message):
    if message.text != '':
        with open('data/location.txt', 'w', encoding='utf-8') as file:
            file.write(message.text)
        bot.send_message(message.chat.id, 'Сохранил текст')
    else:
        bot.send_message(message.chat.id, text=f'данные некорректны')


def edit_photo(message):
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('data/image.jpg', 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, 'Сохранил фото')


def edit_list_players(message):
    with open('data/players.csv', encoding='utf-8') as cvsfile:
        reader = csv.reader(cvsfile)
        spisok_def = [i for i in reader]
    if message.text != '' and message.text.isdigit() and (
            int(message.text) <= len(spisok_def) and int(message.text) > 0):
        spisok_def.pop(int(message.text) - 1)

        with open('data/players.csv', 'w', encoding='utf-8', newline='') as cvsfile:
            writer = csv.writer(cvsfile)
            for line in spisok_def:
                writer.writerow(line)
            bot.send_message(
                message.chat.id,
                f"Великий админ, удалил игрока под номером {message.text}")
    else:
        bot.send_message(message.chat.id, text=f'Ввод некорректен')


@bot.callback_query_handler(func=lambda message: True)
def ans(message):
    chat_id = message.message.chat.id

    if "Информация о следующей игре" == message.data:
        bot.answer_callback_query(message.id)
        with open('data/location.txt', encoding='utf-8') as file:
            x = file.read()
        if x != '':
            bot.send_message(chat_id, x)
        else:
            bot.send_message(chat_id, 'Информации пока что нет')

        with open('data/image.jpg', 'rb') as photo:
            bot.send_photo(chat_id, photo)


    elif "Состав на ближайщую игру" == message.data:
        bot.answer_callback_query(message.id)
        with open('data/players.csv', encoding='utf-8') as cvsfile:
            reader = csv.reader(cvsfile)
            spisok = [' '.join(map(str, i)) for i in reader]
            spisok_ref = [f'{i + 1}) {spisok[i]}' for i in range(len(spisok))]
            if spisok == []:
                bot.send_message(chat_id, f"пока никого нет , будь первым 💪")
            else:
                spisok_req = '\n'.join(map(str, spisok_ref))
                bot.send_message(chat_id, f"""{spisok_req}
        """)


    elif message.data == "Я не играю":
        bot.answer_callback_query(message.id)
        with open('data/players.csv', encoding='utf-8') as cvsfile:
            reader = csv.reader(cvsfile)
            spisok = [i for i in reader]
        if [str(message.from_user.id)[:4] + ' ' + message.from_user.first_name
            ] not in spisok:
            bot.send_message(chat_id,
                             f"{message.from_user.first_name}, тебя нет в списке")
        else:
            spisok = [
                i for i in spisok if i !=
                                     [str(message.from_user.id)[:4] + ' ' + message.from_user.first_name]
            ]
            with open('data/players.csv', 'w', encoding='utf-8', newline='') as cvsfile:
                writer = csv.writer(cvsfile)
                for line in spisok:
                    writer.writerow(line)
                bot.send_message(
                    chat_id,
                    f"{message.from_user.first_name}, удалил тебя из списка")


    elif message.data == "Я играю":
        bot.answer_callback_query(message.id)
        with open('data/players.csv', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            spisok = [i for i in reader]
        if [str(message.from_user.id)[:4] + ' ' + message.from_user.first_name
            ] in spisok:
            bot.send_message(
                chat_id,
                f"{message.from_user.first_name}, ты уже есть в списке")
        else:
            with open('data/players.csv', 'a+', encoding='utf-8',
                      newline='') as csvfile:
                write = csv.writer(csvfile)
                write.writerow(
                    [str(message.from_user.id)[:4] + ' ' + message.from_user.first_name])
                bot.send_message(chat_id,
                                 f"""{message.from_user.first_name}, записал тебя.
(Если у тебя не получается, то не забудь нажать кнопку "Я не играю "🙄)
          """)


def list_commands(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    command = ['Информация о следующей игре', 'Я играю', 'Я не играю', 'Состав на ближайщую игру']
    for i in command:
        keyboard.add(types.InlineKeyboardButton(text=i, callback_data=i))
    return keyboard


bot.polling(non_stop=True, interval=0)
