from source import *


def Main() -> None:
    while True:
        try:
            bot.polling(none_stop=True, interval=1)
        except Exception as e:
            Stamp(f'Error {e} happened', 'e')
            Stamp(traceback.format_exc(), 'e')


def SendMessage(user: int, msg: Union[str, list[str]]) -> None:
    Stamp(f'Sending message to one user {user}', 'i')
    if isinstance(msg, str):
        bot.send_message(user, msg, parse_mode='Markdown')
    elif msg:
        for m in msg:
            bot.send_message(user, m, parse_mode='Markdown')
    else:
        bot.send_message(user, '▪️Нет изменений', parse_mode='Markdown')


def ShowCatalog(message: telebot.types.Message) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for category in PRODUCTS.keys():
        markup.row(telebot.types.KeyboardButton(category))
    bot.send_message(message.from_user.id, 'Выберите категорию:', reply_markup=markup)


def ShowCategory(message: telebot.types.Message) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for product in PRODUCTS[message.text]:
        markup.row(telebot.types.KeyboardButton(product))
    bot.send_message(message.from_user.id, 'Выберите товар:', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def MessageAccept(message: telebot.types.Message) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    if message.text == '/start':
        SendMessage(message.from_user.id, f'Привет, {message.from_user.first_name}!')
        ShowCatalog(message)
    elif message.text in PRODUCTS.keys():
        ShowCategory(message)
    else:
        SendMessage(message.from_user.id, 'Неизвестная опция...')


if __name__ == '__main__':
    Main()
