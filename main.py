from source import *


def Main() -> None:
    while True:
        try:
            bot.polling(none_stop=True, interval=1)
        except Exception as e:
            Stamp(f'Error {e} happened', 'e')
            Stamp(traceback.format_exc(), 'e')


def ShowButtons(message: telebot.types.Message, buttons: tuple, answer: str, handler: Callable = None) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for btn in buttons:
        markup.row(telebot.types.KeyboardButton(btn))
    bot.send_message(message.from_user.id, answer, reply_markup=markup)


def ShowInfo(row: int) -> str:
    service = BuildService()
    info = GetSector(f'A{row}', f'M{row}', service, PRODUCTS_SHEET_NAME, SHEET_ID)[0]
    msg = f'*Модель*: {info[0]}\n' \
          f'*Описание*: {info[2]}\n' \
          f'*Остаток*: {info[5]} штук\n' \
          f'*Цена*: {info[6]} рублей\n' \
          f'*М^2 в упаковке*: {info[7]}\n' \
          f'*Защитный слой*: {info[8]}\n' \
          f'*Класс износостойкости*: {info[9]}\n' \
          f'*Производитель*: {info[10]}\n' \
          f'*Артикул*: {info[11]}\n'
    return msg


def SearchByID(message: telebot.types.Message) -> None:
    service = BuildService()
    ids = GetSector('L2', 'L100', service, PRODUCTS_SHEET_NAME, SHEET_ID)
    ids = [item for sublist in ids for item in sublist]
    if message.text in ids:
        bot.send_message(message.from_user.id, ShowInfo(ids.index(message.text) + 2), parse_mode='Markdown')
    else:
        bot.send_message(message.from_user.id, f'Не найдено товара по ID {message.text}')


def ListContacts() -> str:
    service = BuildService()
    contacts = GetSector('A2', 'B5', service, CONTACTS_SHEET_NAME, SHEET_ID)
    msg = ''
    for contact in contacts:
        msg += f'▫️ *{contact[0]}*: {contact[1]}\n'
    return msg


def ShowCategories() -> tuple:
    service = BuildService()
    categories = GetSector('B2', 'B100', service, PRODUCTS_SHEET_NAME, SHEET_ID)
    categories = [item for sublist in categories for item in sublist]
    categories = list(set(categories))
    categories.insert(0, OPERATE_BTNS[0])
    categories.append(OPERATE_BTNS[1])
    return tuple(categories)


@bot.message_handler(content_types=['text'])
def MessageAccept(message: telebot.types.Message) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    if message.text == '/start':
        bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}!')
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')
    # Catalogue option
    elif message.text == OPERATE_BTNS[0]:
        bot.send_message(message.from_user.id, 'Введите ID товара:')
        bot.register_next_step_handler(message, SearchByID)
    elif message.text == OPERATE_BTNS[1]:
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')
    elif message.text == MENU_BTNS[0]:
        ShowButtons(message, ShowCategories(), 'Выберите элемент каталога:')
    # Contacts options
    elif message.text == MENU_BTNS[1]:
        bot.send_message(message.from_user.id, ListContacts(), parse_mode='Markdown')
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')
    # Operator connection
    elif message.text == MENU_BTNS[2]:
        bot.send_message(message.from_user.id, 'Сведения переданы оператору. С Вами свяжутся в ближайшее время!')
        bot.send_message(GROUP_ID, f'ID: {message.from_user.id}\n'
                                   f'First name: {message.from_user.first_name}\n'
                                   f'Second name: {message.from_user.last_name}\n'
                                   f'Username: {message.from_user.username}\n'
                        )
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')
    else:
        bot.send_message(message.from_user.id, 'Неизвестная опция...')
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')


if __name__ == '__main__':
    Main()
