import telebot
from telebot import types
import csv

import setting

bot = telebot.TeleBot(setting.TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    btn2 = types.KeyboardButton("❓ Инфо о футболе")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text='Выберите команду', reply_markup=markup)


@bot.message_handler(content_types=['text', 'photo'])
def func(message):
    if message.text == "👋 Поздороваться":
        url = 'https://t.me/+UEt2XfUHsFVjMzky'
        bot.send_message(
            message.chat.id,
            text=
            f"""Привет {message.chat.first_name}👋
Спасибо, что присоединился к нам!😎

Присоединяйся к нашей группе {url}""")
    elif message.text == "❓ Инфо о футболе":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("#Состав_на_ближайший_четверг")
        btn2 = types.KeyboardButton("#Локация")
        btn3 = types.KeyboardButton("#Я_играю")
        btn4 = types.KeyboardButton("#Я_не_играю")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, btn3, btn4, back)
        bot.send_message(message.chat.id,
                         text="Задай мне вопрос",
                         reply_markup=markup)

    elif message.text == "#Я_играю":
        with open('players.csv', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            spisok = [i for i in reader]
        if [str(message.from_user.id)[:4] + ' ' + message.from_user.first_name
            ] in spisok:
            bot.send_message(
                message.chat.id,
                f"{message.from_user.first_name}, ты уже есть в списке")
        else:
            with open('players.csv', 'a+', encoding='utf-8',
                      newline='') as csvfile:
                write = csv.writer(csvfile)
                write.writerow(
                    [str(message.from_user.id)[:4] + ' ' + message.from_user.first_name])
                bot.send_message(message.chat.id,
                                 f"""{message.from_user.first_name}, записал тебя.
(Если у тебя не получается, то не забудь нажать кнопку "Я не играю "🙄)
  """)



    elif message.text == "#Я_не_играю":
        with open('players.csv', encoding='utf-8') as cvsfile:
            reader = csv.reader(cvsfile)
            spisok = [i for i in reader]
        if [str(message.from_user.id)[:4] + ' ' + message.from_user.first_name
            ] not in spisok:
            bot.send_message(message.chat.id,
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
                    message.chat.id,
                    f"{message.from_user.first_name}, удалил тебя из списка")


    elif message.text == "#Состав_на_ближайший_четверг":
        with open('players.csv', encoding='utf-8') as cvsfile:
            reader = csv.reader(cvsfile)
            spisok = [' '.join(map(str, i)) for i in reader]
            spisok_ref = [f'{i + 1}) {spisok[i]}' for i in range(len(spisok))]
            if spisok == []:
                bot.send_message(message.chat.id, f"пока никого нет , будь первым 💪")
            else:
                spisok_req = '\n'.join(map(str, spisok_ref))
                bot.send_message(message.chat.id, f"""{spisok_req}
""")

    elif message.text == '#Локация':
        bot.send_message(message.chat.id, f"""Адрес:
Г. Москва, улица Чертановская дом 7 корпус 3. Крытый манеж размеры 73.5 на 36.4

Время и дата:
Каждый четверг с 21-00 до 22-30

Стоимость:
9000 рублей, за полтора часа

Организатор:
По всем вопросам обращаться +79685272288
            """)
        photo = open('вход.jpg', 'rb')
        bot.send_photo(message.chat.id, photo)


    elif message.text == 'обновить список':
        if message.from_user.id == 415817424:
            with open('players.csv', 'w', encoding='utf-8') as cvsfile:
                drop_list = csv.reader(cvsfile)
            bot.send_message(message.chat.id, "Список обновлен")


    elif message.text == "Вернуться в главное меню":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button1 = types.KeyboardButton("👋 Поздороваться")
        button2 = types.KeyboardButton("❓ Инфо о футболе")
        markup.add(button1, button2)
        bot.send_message(message.chat.id,
                         text="Вы вернулись в главное меню",
                         reply_markup=markup)
    else:
        pass


bot.polling(non_stop=True, interval=0)
