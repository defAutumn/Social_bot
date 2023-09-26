"""
все клавиатуры, используемые ботов. В этом файле будут находиться абсолютно
все клавиатуры, как статические, так и динамически генерируемые через функции
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,\
    ReplyKeyboardMarkup, ReplyKeyboardRemove

menu = [
    [
        InlineKeyboardButton(text="Отправить обращение", callback_data="send_form")
    ],
    [
        InlineKeyboardButton(text="Мои обращения", callback_data="get_forms")
    ],
    [
        InlineKeyboardButton(text="Помощь", callback_data="help"),
        InlineKeyboardButton(text="Ссылки", callback_data="links")
    ],
]

categories_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Благоустройство',
            callback_data='landscaping'
        )
    ],
    [
        InlineKeyboardButton(
            text='Мусор',
            callback_data='garbage'
        )
    ],
    [
        InlineKeyboardButton(
            text='Общественный транспорт',
            callback_data='public_transport'
        )
    ]
])

transport_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Маршрутное такси',
            callback_data='minibus'
        )
    ],
    [
        InlineKeyboardButton(
            text='Автобус',
            callback_data='bus'
        )
    ],
    [
        InlineKeyboardButton(
            text='Троллейбус',
            callback_data='trolleybus'
        )
    ],
    [
        InlineKeyboardButton(
            text='Трамвай',
            callback_data='tram'
        )
    ]
])

menu = InlineKeyboardMarkup(inline_keyboard=menu)
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Выйти в меню")]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Выйти в меню", callback_data="menu")]])
