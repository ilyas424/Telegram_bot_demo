import telebot
from telebot import types
import csv

import setting

bot = telebot.TeleBot(setting.TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, "Hello",
        reply_markup=keyboard()
    )


@bot.message_handler(content_types=['text'])
def send_anytext(message):
    chat_id = message.chat.id
    if message.text == 'command':
        text = 'Выберите команду'
        bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=balance_key(chat_id))



@bot.callback_query_handler(func=lambda message: True)
def ans(message):
    chat_id = message.message.chat.id

    if "Локация" == message.data:
        bot.send_message(chat_id, f"""Адрес:
Г. Москва, улица Чертановская дом 7 корпус 3. Крытый манеж размеры 73.5 на 36.4

Время и дата:
Каждый четверг с 21-00 до 22-30

Стоимость:
9000 рублей, за полтора часа

Организатор:
По всем вопросам обращаться +79685272288
            """)
        photo = open('вход.jpg', 'rb')
        bot.send_photo(chat_id, photo)


    elif "Состав на ближайший четверг" == message.data:
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


def keyboard():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn = types.KeyboardButton('command')
    markup.add(btn)
    return markup


def balance_key(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    command = ['Локация', 'Я играю', 'Я не играю', 'Состав на ближайший четверг']
    for i in command:
        keyboard.add(types.InlineKeyboardButton(text=i, callback_data="{0}".format(i)))
    return keyboard


bot.polling(non_stop=True, interval=0)