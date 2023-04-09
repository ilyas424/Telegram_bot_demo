import telebot
from telebot import types
import csv

import setting

bot = telebot.TeleBot(setting.TOKEN)


@bot.message_handler(commands=['start'])
def send_anytext(message):
    chat_id = message.chat.id
    text = 'Выберите команду'
    bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=list_commands(chat_id))


@bot.message_handler(commands=['admin'])
def is_admin(message):
    if message.from_user.id == setting.ilyas or message.from_user.id == setting.ilsur:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("Изменить раздел локация")
        btn2 = types.KeyboardButton("Удалить игрока")
        btn3 = types.KeyboardButton("Обновить список")
        btn4 = types.KeyboardButton("Убрать кнопки")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, text='Выберите команду', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text='Недостаточно прав доступа')


@bot.message_handler(content_types=['text'])
def send_call(message):
    chat_id = message.chat.id
    if message.text == '@football_tatarlar_Bot':
        text = 'Выберите команду'
        bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=list_commands(chat_id))

    if message.text == 'Изменить раздел локация' and (message.from_user.id == setting.ilyas or message.from_user.id == setting.ilsur):
        bot.send_message(message.chat.id, text='введите новый текст')
        bot.register_next_step_handler(message, edit_data)

    if message.text == 'Удалить игрока' and (message.from_user.id == setting.ilyas or message.from_user.id == setting.ilsur):
        with open('players.csv', encoding='utf-8') as cvsfile:
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

    if message.text == 'Обновить список' and (message.from_user.id == setting.ilyas or message.from_user.id == setting.ilsur):
        with open('players.csv', 'w', encoding='utf-8') as cvsfile:
            csv.reader(cvsfile)
        bot.send_message(message.chat.id, "Список обновлен")

    if message.text == 'Убрать кнопки' and (message.from_user.id == setting.ilyas or message.from_user.id == setting.ilsur):
        a = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Убрал', reply_markup=a)
        
def edit_data(message):
    if message.text != '':
        with open('location.txt', 'w', encoding='utf-8') as file:
            file.write(message.text)
        bot.send_message(message.chat.id, text=f'сохранил!')
    else:
        bot.send_message(message.chat.id, text=f'Вы ничего не ввели')


def edit_list_players(message):
    with open('players.csv', encoding='utf-8') as cvsfile:
        reader = csv.reader(cvsfile)
        spisok_def = [i for i in reader]
    if message.text != '' and message.text.isdigit() and (int(message.text) <= len(spisok_def) and int(message.text) > 0) :
        spisok_def.pop(int(message.text)-1)

        with open('players.csv', 'w', encoding='utf-8', newline='') as cvsfile:
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

    if "Локация" == message.data:
        bot.answer_callback_query(message.id)
        with open('location.txt', encoding='utf-8') as file:
            x = file.read()
        if x != '':
            bot.send_message(chat_id, x)
        else:
            bot.send_message(chat_id, 'Информации пока что нет')

        with open('вход.jpg', 'rb') as photo:
            bot.send_photo(chat_id, photo)


    elif "Состав на ближайший четверг" == message.data:
        bot.answer_callback_query(message.id)
        with open('players.csv', encoding='utf-8') as cvsfile:
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
        with open('players.csv', encoding='utf-8') as cvsfile:
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
            with open('players.csv', 'w', encoding='utf-8', newline='') as cvsfile:
                writer = csv.writer(cvsfile)
                for line in spisok:
                    writer.writerow(line)
                bot.send_message(
                    chat_id,
                    f"{message.from_user.first_name}, удалил тебя из списка")


    elif message.data == "Я играю":
        bot.answer_callback_query(message.id)
        with open('players.csv', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            spisok = [i for i in reader]
        if [str(message.from_user.id)[:4] + ' ' + message.from_user.first_name
            ] in spisok:
            bot.send_message(
                chat_id,
                f"{message.from_user.first_name}, ты уже есть в списке")
        else:
            with open('players.csv', 'a+', encoding='utf-8',
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
    command = ['Локация', 'Я играю', 'Я не играю', 'Состав на ближайший четверг']
    for i in command:
        keyboard.add(types.InlineKeyboardButton(text=i, callback_data="{0}".format(i)))
    return keyboard


bot.polling(non_stop=True, interval=0)
