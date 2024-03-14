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


def ShowButtons(message: telebot.types.Message, buttons: tuple, answer: str, handler: Callable = None) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for btn in buttons:
        markup.row(telebot.types.KeyboardButton(btn))
    bot.send_message(message.from_user.id, answer, reply_markup=markup)


def SearchByID(message: telebot.types.Message) -> None:
    if message.text in 'да':
        SendMessage(message.from_user.id, 'Нашёл!')
    else:
        SendMessage(message.from_user.id, 'Такого нет(')


@bot.message_handler(content_types=['text'])
def MessageAccept(message: telebot.types.Message) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    if message.text == '/start':
        SendMessage(message.from_user.id, f'Привет, {message.from_user.first_name}!')
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')
    # Catalogue option
    elif message.text == CATALOGUE_BTNS[0]:
        SendMessage(message.from_user.id, 'Введите ID товара:')
        bot.register_next_step_handler(message, SearchByID)
    elif message.text == CATALOGUE_BTNS[-1]:
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')
    elif message.text == MENU_BTNS[0]:
        ShowButtons(message, CATALOGUE_BTNS, 'Выберите элемент каталога:')
    # Contacts options
    elif message.text == MENU_BTNS[1]:
        SendMessage(message.from_user.id, 'Звоните Ромке 89152014847')
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')
    # Operator connection
    elif message.text == MENU_BTNS[2]:
        SendMessage(message.from_user.id, 'Переключаю на оператора...')
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')
    else:
        SendMessage(message.from_user.id, 'Неизвестная опция...')
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')


if __name__ == '__main__':
    Main()
