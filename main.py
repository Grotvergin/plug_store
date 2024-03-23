from source import *


def Main() -> None:
    while True:
        try:
            bot.polling(none_stop=True, interval=1)
        except Exception as e:
            Stamp(f'Error {e} happened', 'e')
            Stamp(traceback.format_exc(), 'e')


def ShowButtons(message: telebot.types.Message, buttons: tuple, answer: str) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for btn in buttons:
        markup.row(telebot.types.KeyboardButton(btn))
    bot.send_message(message.from_user.id, answer, reply_markup=markup)


def ShowInfo(row: int) -> str:
    info = GetSector(f'A{row}', f'L{row}', service, PRODUCTS_SHEET_NAME, SHEET_ID)[0]
    msg = f'*Модель*: {info[0]}\n' \
          f'*Описание*: {info[2]}\n' \
          f'*Остаток*: {info[5]} штук\n' \
          f'*Цена*: {info[6]} рублей\n' \
          f'*М^2 в упаковке*: {info[7]}\n' \
          f'*Защитный слой*: {info[8]}\n' \
          f'*Класс износостойкости*: {info[9]}\n' \
          f'*Производитель*: {info[10]}\n'
    return msg


def SearchByID(message: telebot.types.Message) -> None:
    ids = GetSector('A2', 'A1000', service, PRODUCTS_SHEET_NAME, SHEET_ID)
    ids = [item for sublist in ids for item in sublist]
    search_text = message.text.lower()
    matching_ids = [id for id in ids if search_text in id.lower()]
    if matching_ids:
        ShowButtons(message, OPERATE_BTNS, f'Найдены {len(matching_ids)} товар(ов) по ID {message.text}')
        for id in matching_ids:
            message.data = 'S' + str(ids.index(id) + 2)
            ShowInfoGood(message)
    else:
        bot.send_message(message.from_user.id, f'Не найдено товара по ID {message.text}')
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')


def ListContacts() -> str:
    contacts = GetSector('A2', 'B5', service, CONTACTS_SHEET_NAME, SHEET_ID)
    msg = ''
    for contact in contacts:
        msg += f'▫️ *{contact[0]}*: {contact[1]}\n'
    return msg


def ShowCategories() -> tuple:
    categories = GetSector('B2', 'B1000', service, PRODUCTS_SHEET_NAME, SHEET_ID)
    categories = [item for sublist in categories for item in sublist]
    categories = list(set(categories))
    categories.insert(0, OPERATE_BTNS[0])
    categories.append(OPERATE_BTNS[1])
    return tuple(categories)


def ChosenCategory(message: telebot.types.Message, categories_available: tuple) -> None:
    if message.text in categories_available[1:-1]:
        ShowButtons(message, OPERATE_BTNS, f'Выбрана категория "{message.text}"')
        info = GetSector('A2', 'B1000', service, PRODUCTS_SHEET_NAME, SHEET_ID)
        appropriate_goods = {}
        for i, row in enumerate(info):
            if row[1] == message.text:
                appropriate_goods[row[0]] = i
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        for good in appropriate_goods.keys():
            keyboard.add(telebot.types.InlineKeyboardButton(good, callback_data='S' + str(appropriate_goods[good] + 2)))
        bot.send_message(message.from_user.id, f'Доступные товары:', reply_markup=keyboard)
    else:
        MessageAccept(message)


def DownloadImage(row: int) -> None:
    if os.path.isfile(f'{row}.png'):
        Stamp(f'File {row}.png exists', 'i')
        return
    file_id = '1xQy93hKnSca8h5xfC3DDrxAgIU-T5wwl'
    request = driver.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        Stamp(f'Downloading file {row}.png {int(status.progress() * 100)}%', 'w')
    with open(f'{row}.png', 'wb') as f:
        f.write(fh.getvalue())
    Stamp(f'File {row}.png was downloaded', 's')


def OrderQuantity(message: telebot.types.Message, index_good: str, type_order: str):
    if message.text.isdigit():
        name_good = GetSector(f'A{index_good}', f'A{index_good}', service, PRODUCTS_SHEET_NAME, SHEET_ID)[0][0]
        ShowButtons(message, OPERATE_BTNS, f'Вы заказали {message.text} {name_good}. С вами вскоре свяжутся!')
        bot.send_message(GROUP_ID, f'{type_order}\n'
                                   f'Название: {name_good}\n'
                                   f'Количество: {message.text}\n'
                                   f'ID: {message.from_user.id}\n'
                                   f'First name: {message.from_user.first_name}\n'
                                   f'Second name: {message.from_user.last_name}\n'
                                   f'Username: {message.from_user.username}\n')
    else:
        bot.send_message(message.from_user.id, 'Количество товаров не распознано, попробуйте ещё раз:')
        FastOrder(message, index_good, type_order)


@bot.callback_query_handler(func=lambda call: call.data.startswith('S'))
def ShowInfoGood(call: telebot.types.CallbackQuery):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    for btn in BASKET_BTNS.keys():
        keyboard.add(telebot.types.InlineKeyboardButton(btn, callback_data=BASKET_BTNS[btn] + call.data[1:]))
    DownloadImage(int(call.data[1:]))
    with open(f'{call.data[1:]}.png', 'rb') as photo:
        bot.send_photo(call.from_user.id, photo, caption=ShowInfo(int(call.data[1:])), reply_markup=keyboard, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data.startswith('F'))
def FastOrder(call: telebot.types.CallbackQuery):
    bot.send_message(call.from_user.id, 'Введите количество товаров, которое желаете заказать:')
    bot.register_next_step_handler(call.message, OrderQuantity, call.data[1:], 'Быстрый заказ')


@bot.callback_query_handler(func=lambda call: call.data.startswith('B'))
def BasketAdd(call: telebot.types.CallbackQuery):
    bot.send_message(call.from_user.id, 'Введите количество товаров, которое желаете заказать:')
    bot.register_next_step_handler(call.message, OrderQuantity, call.data[1:], 'Добавление в корзину')


@bot.callback_query_handler(func=lambda call: call.data.startswith('D'))
def ShowFullDescription(call: telebot.types.CallbackQuery):
    bot.send_message(call.from_user.id, 'Тут должно быть полное описание...')


@bot.message_handler(content_types=['text'])
def MessageAccept(message: telebot.types.Message) -> None:
    Stamp(f'User {message.from_user.id} requested {message.text}', 'i')
    if message.text == '/start':
        bot.send_message(message.from_user.id, f'Привет, {message.from_user.first_name}!')
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')
    elif message.text == OPERATE_BTNS[0]:
        bot.send_message(message.from_user.id, 'Введите ID товара:')
        bot.register_next_step_handler(message, SearchByID)
    elif message.text == OPERATE_BTNS[1]:
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')
    elif message.text == MENU_BTNS[0] or message.text == OPERATE_BTNS[2]:
        categories = ShowCategories()
        ShowButtons(message, categories, 'Выберите элемент каталога:')
        bot.register_next_step_handler(message, ChosenCategory, categories)
    elif message.text == MENU_BTNS[1]:
        bot.send_message(message.from_user.id, ListContacts(), parse_mode='Markdown')
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')
    elif message.text == MENU_BTNS[2]:
        bot.send_message(message.from_user.id, 'Сведения переданы оператору. С Вами свяжутся в ближайшее время!')
        bot.send_message(GROUP_ID, f'Связь с оператором\n'
                                   f'ID: {message.from_user.id}\n'
                                   f'First name: {message.from_user.first_name}\n'
                                   f'Second name: {message.from_user.last_name}\n'
                                   f'Username: {message.from_user.username}\n')
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')
    else:
        bot.send_message(message.from_user.id, 'Неизвестная опция...')
        ShowButtons(message, MENU_BTNS, 'Выберите действие:')


if __name__ == '__main__':
    Main()
