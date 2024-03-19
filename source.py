from common import *

config, _ = ParseConfig()
bot = telebot.TeleBot(config['DEFAULT']['Token'])
SHEET_ID = config['DEFAULT']['SheetID']
GROUP_ID = config['DEFAULT']['GroupID']
MENU_BTNS = ('Каталог', 'Контакты', 'Связь с оператором')
OPERATE_BTNS = ('Поиск товаров', 'В меню')
CONTACTS_SHEET_NAME = 'Contacts'
PRODUCTS_SHEET_NAME = 'Products'
