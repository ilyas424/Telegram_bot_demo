import telebot
from telebot import types
import csv

import  setting

bot = telebot.TeleBot(setting.TOKEN)
spisok_players = []


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    btn2 = types.KeyboardButton("❓ Инфо о футболе")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Я тестовый бот".format(
                         message.from_user),
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == "👋 Поздороваться":
        url = 'https://t.me/+PJwnI9BhtiFlYWUy'
        bot.send_message(
            message.chat.id,
            text=
            f"""Привеет {message.chat.first_name}👋
Спасибо что присоеденился к нам!😎

Присоединяйся к нашей группе {url}""")
    elif message.text == "❓ Инфо о футболе":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("Состав на ближайшею пятницу")
        btn2 = types.KeyboardButton("Сколько свободных мест")
        btn3 = types.KeyboardButton("Я играю")
        btn4 = types.KeyboardButton("Я не играю")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, btn3, btn4, back)
        bot.send_message(message.chat.id,
                         text="Задай мне вопрос",
                         reply_markup=markup)

    elif message.text == "Я играю":
        with open('players.csv', encoding='utf-8') as cvsfile:
            reader = csv.reader(cvsfile)
            spisok = [i for i in reader]
            if len(spisok) >= 18:
                bot.send_message(message.chat.id,
                                 f"{message.from_user.first_name}, мест не осталось")
            elif [str(message.from_user.id) + ' ' + message.from_user.first_name
                  ] in spisok:
                bot.send_message(
                    message.chat.id,
                    f"{message.from_user.first_name}, ты уже есть в списке")
            else:
                with open('players.csv', 'a+', encoding='utf-8',
                          newline='') as cvsfile:
                    write = csv.writer(cvsfile)
                    write.writerow(
                        [str(message.from_user.id) + ' ' + message.from_user.first_name])
                    bot.send_message(message.chat.id,
                                     f"""{message.from_user.first_name}, записал тебя.
(Если у тебя не получается, то не забудь нажать кнопку "Я не играю 🙄")
  """)

    elif message.text == "Я не играю":
        with open('players.csv', encoding='utf-8') as cvsfile:
            reader = csv.reader(cvsfile)
            spisok = [i for i in reader]
            if [str(message.from_user.id) + ' ' + message.from_user.first_name
                ] not in spisok:
                bot.send_message(message.chat.id,
                                 f"{message.from_user.first_name}, тебя нет в списке")
            else:
                spisok = [
                    i for i in spisok if i !=
                                         [str(message.from_user.id) + ' ' + message.from_user.first_name]
                ]
                with open('players.csv', 'w', encoding='utf-8') as cvsfile:
                    writer = csv.writer(cvsfile)
                    for line in spisok:
                        writer.writerow(line)
                    bot.send_message(
                        message.chat.id,
                        f"{message.from_user.first_name}, удалил тебя из списка")

    elif message.text == "Состав на ближайшею пятницу":
        with open('players.csv', encoding='utf-8', newline='') as cvsfile:
            reader = csv.reader(cvsfile)
            spisok = [' '.join(map(str, i)) for i in reader]
            if spisok == []:
                bot.send_message(message.chat.id, f"пока никого нет , будь первым 💪")
            else:
                spisok_req = '\n'.join(map(str, spisok))
                bot.send_message(message.chat.id, f"{spisok_req}")

    elif message.text == "Сколько свободных мест":
        with open('players.csv', encoding='utf-8') as cvsfile:
            reader = csv.reader(cvsfile)
            spisok = [i for i in reader]
            if len(spisok) == 18:
                bot.send_message(message.chat.id, text=f"Свободных мест нет 😫")
            else:
                bot.send_message(message.chat.id, text=f"Осталось {18 - len(spisok)}")

    elif message.text == "Вернуться в главное меню":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button1 = types.KeyboardButton("👋 Поздороваться")
        button2 = types.KeyboardButton("❓ Инфо о футболе")
        markup.add(button1, button2)
        bot.send_message(message.chat.id,
                         text="Вы вернулись в главное меню",
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id,
                         text="На такую комманду я не запрограммировал..😞")


bot.polling(non_stop=True, interval=0)

