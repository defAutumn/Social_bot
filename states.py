"""
будет хранить вспомогательные классы для FSM (машины состояний),
а также фабрики Callback Data для кнопок Inline клавиатур
"""

from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    category = State()


class LandscapingGarbageForm(StatesGroup):
    location = State()
    description = State()
    photo_id = State()


class TransportForm(StatesGroup):
    subcategory = State()
    number = State()
    description = State()
    photo_id = State()