import random
import asyncio
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import TransportForm, LandscapingGarbageForm, Form, GetFormForm
from typing import Any, Dict
from ..db.models import PostTransport, PostLandscaping, PostGarbage, PostFreeForm
from sqlalchemy.ext.asyncio import AsyncSession
import kb
from sqlalchemy import select

form_router = Router()


# -----------------------------------------------------

categories = {
    'landscaping': ['Благоустройство', 'Введите локацию', PostLandscaping],
    'public_transport': ['Общественный транспорт', 'Напишите номер маршрута', PostTransport],
    'garbage': ['Мусор', 'Введите локацию', PostGarbage],
    'free_form': ['Свободная форма', 'Введите локацию или название учреждения', PostFreeForm]}

subcategories = {
    'minibus': 'Маршрутное такси',
    'tram': 'Трамвай',
    'trolleybus': 'Троллейбус',
    'bus': 'Автобус'
}

# -----------------------------------------------------


@form_router.message(Command("start"))
async def command_start(message: Message) -> None:
    await message.answer("Добро пожаловать!")
    await asyncio.sleep(2)
    await message.answer("Этот бот создан для проекта <tg-spoiler>(название мы еще не придумали 🤡🤡🤡)</tg-spoiler>\n\n"
                         "Он позволяет отправить обращение по какой-либо проблеме так же легко, как отправить сообщение\n\n"
                         "Будем рады, если вы нас поддержите и отправите хотя бы одно обращение. <b>Каждое</b> обращение будет"
                         " обработано и направлено в соотвествующую инстанцию. Чем больше вы отправите, тем лучше ♥\n\n"
                         "Ссылка на <a href='https://forms.gle/QmyMuCbLECuY7wSp9'>анкету</a>\n\n"
                         "<b>Все обращения и их статус будут опубликованы <a href='https://t.me/TulikCoolPublick'>тут</a></b>\n\n",
                         parse_mode=ParseMode.HTML)
    await asyncio.sleep(15)
    await message.answer("Меню", reply_markup=kb.menu)


@form_router.message(F.text == "Меню")
@form_router.message(F.text == "Выйти в меню")
async def command_menu(message: Message) -> None:
    await message.answer("Меню", reply_markup=kb.menu)


@form_router.callback_query(F.data == "links")
async def get_links(message: Message) -> None:
    await message.message.answer(
        "Открытый регион: `https://or71.ru/`\n"
        "Паблик: https://t.me/TulikCoolPublick",
        reply_markup=kb.exit_kb,
    )


@form_router.callback_query(F.data == "contacts")
async def get_links(message: Message) -> None:
    await message.message.answer("Для жалоб и предложений: `defautumn@mail.ru`", reply_markup=kb.exit_kb)


@form_router.callback_query(F.data == "get_forms")
async def get_form(message: Message, state: FSMContext) -> None:
    await state.set_state(GetFormForm.post_id)
    await message.message.answer("Введите ID", reply_markup=kb.exit_kb)


@form_router.message(GetFormForm.post_id)
async def process_final(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = message.text.split('.')
    await state.clear()
    result = (await session.execute(select(categories[data[0]][2])
                                    .where(categories[data[0]][2].post_id == int(data[1])))).first()
    post = result[0].__dict__
    if data[0] in ['garbage', 'landscaping', 'free_form']:
        await message.answer_photo(post['photo_id'], caption=f'Локация: {post["location"]}\n'
                                                             f'Описание: {post["description"]}\n'
                                                             f'Дата отправки: {post["published"]}\n'
                                                             f'Статус: {post["status"]}')
    else:
        await message.answer_photo(post['photo_id'], caption=f'Вид: {subcategories[post["subcategory"]]}\n'
                                                             f'Номер: {post["number"]}\n'
                                                             f'Описание: {post["description"]}\n'
                                                             f'Дата отправки: {post["published"]}\n'
                                                             f'Статус: {post["status"]}')


@form_router.callback_query(F.data == "send_form")
async def process_category(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.category)
    await message.message.answer("Выбери категорию", reply_markup=kb.categories_kb,)


@form_router.callback_query(F.data == "landscaping")
async def process_location(clbk: CallbackQuery, state: FSMContext) -> None:
    await choose(clbk)
    await process_inner(clbk, state)


@form_router.callback_query(F.data == "garbage")
async def process_location(clbk: CallbackQuery, state: FSMContext) -> None:
    await choose(clbk)
    await process_inner(clbk, state)


@form_router.callback_query(F.data == "free_form")
async def process_location(clbk: CallbackQuery, state: FSMContext) -> None:
    await choose(clbk)
    await process_inner(clbk, state)


@form_router.message(LandscapingGarbageForm.location)
async def process_like_write_bots(message: Message, state: FSMContext) -> None:
    if message.text:
        await state.update_data(location=message.text)
        await state.set_state(LandscapingGarbageForm.description)
        await message.answer("Опишите проблему", reply_markup=kb.exit_kb)
    else:
        await uncorrect_input(message)


@form_router.message(LandscapingGarbageForm.description)
async def process_photo(message: Message, state: FSMContext) -> None:
    if message.text:
        await state.update_data(description=message.text)
        await state.set_state(LandscapingGarbageForm.photo_id)
        await message.answer('Пришлите фотографию\nЕсли фотографии нет, то отправьте любой символ',
                             reply_markup=kb.exit_kb)
    else:
        await uncorrect_input(message)


@form_router.message(LandscapingGarbageForm.photo_id)
async def process_final(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if message.photo:
        data = await state.update_data(photo_id=message.photo[-1].file_id)
        await state.clear()
        await show_summary(message=message, data=data, session=session)
    elif message.text:
        data = await state.update_data(
            photo_id='https://www.meme-arsenal.com/memes/3e9720428bb388bc7a914790438cc779.jpg'
        )
        await state.clear()
        await show_summary(message=message, data=data, session=session)
    else:
        await uncorrect_input(message)


@form_router.callback_query(F.data == "public_transport")
async def process_location(clbk: CallbackQuery, state: FSMContext) -> None:
    await choose(clbk)
    await process_inner(clbk, state)


@form_router.callback_query(F.data == "tram")
async def process_number(clbk: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(subcategory=clbk.data)
    await state.set_state(TransportForm.number)
    await get_number(clbk)


@form_router.callback_query(F.data == "bus")
async def process_number(clbk: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(subcategory=clbk.data)
    await state.set_state(TransportForm.number)
    await get_number(clbk)


@form_router.callback_query(F.data == "trolleybus")
async def process_number(clbk: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(subcategory=clbk.data)
    await state.set_state(TransportForm.number)
    await get_number(clbk)


@form_router.callback_query(F.data == "minibus")
async def process_number(clbk: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(subcategory=clbk.data)
    await state.set_state(TransportForm.number)
    await get_number(clbk)


@form_router.message(TransportForm.number)
async def process_photo(message: Message, state: FSMContext) -> None:
    if message.text:
        await state.update_data(number=message.text)
        await state.set_state(TransportForm.description)
        await message.answer('Опиши проблему', reply_markup=kb.exit_kb)
    else:
        await uncorrect_input(message)


@form_router.message(TransportForm.description)
async def process_photo(message: Message, state: FSMContext) -> None:
    if message.text:
        await state.update_data(description=message.text)
        await state.set_state(TransportForm.photo_id)
        await message.answer('Пришлите фотографию\nЕсли фотографии нет, то отправьте любой символ',
                             reply_markup=kb.exit_kb)
    else:
        await uncorrect_input(message)


@form_router.message(TransportForm.photo_id)
async def process_final(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if message.photo:
        data = await state.update_data(photo_id=message.photo[-1].file_id)
        await state.clear()
        await show_summary(message=message, data=data, session=session)
    elif message.text:
        data = await state.update_data(
            photo_id='https://www.meme-arsenal.com/memes/3e9720428bb388bc7a914790438cc779.jpg'
        )
        await state.clear()
        await show_summary(message=message, data=data, session=session)
    else:
        await uncorrect_input(message)


async def process_inner(clbk, state):
    await state.update_data(category=clbk.data)
    if clbk.data in ['landscaping', 'garbage', 'free_form']:
        await state.set_state(LandscapingGarbageForm.location)
        await clbk.message.answer(categories[clbk.data][1], reply_markup=kb.exit_kb)
    elif clbk.data == 'public_transport':
        await state.set_state(TransportForm.subcategory)
        await clbk.message.answer('Выберите вид транспорта', reply_markup=kb.transport_kb)
        await clbk.message.answer('', reply_markup=kb.exit_kb)


async def choose(clbk):
    await clbk.message.answer(f'Вы выбрали категорию: {categories[clbk.data][0]}')


async def choose_subcategory(clbk):
    await clbk.message.answer(f'Вид транспорта: {subcategories[clbk.data]}')


async def get_number(clbk):
    await clbk.message.answer('Введите номер маршрута', reply_markup=kb.exit_kb)


async def show_summary(message: Message, data: Dict[str, Any], session: AsyncSession) -> None:
    category = data["category"]
    description = data['description']
    photo_id = data['photo_id']

    if category == 'public_transport':

        subcategory = data['subcategory']
        number = data['number']

        await session.merge(PostTransport(
            user_id=message.from_user.id,
            subcategory=subcategory,
            number=number,
            description=description,
            photo_id=photo_id,
            status='Принято'
        ))
        await session.commit()

        result = (await session.execute(select(PostTransport).
                                        where(PostTransport.user_id == message.from_user.id))).all()
        get_id = result[-1][0].__dict__['post_id']

    elif category in ['landscaping', 'garbage', 'free_form']:

        location = data['location']

        await session.merge(categories[category][2](
            user_id=message.from_user.id,
            location=location,
            description=description,
            photo_id=photo_id,
            status='Принято'
        ))
        await session.commit()

        result = (await session.execute(select(categories[category][2])
                                        .where(categories[category][2].user_id == message.from_user.id))).all()
        get_id = result[-1][0].__dict__['post_id']

    await message.answer(f"Большое спасибо! Ваше обращение принято! :)")
    await message.answer(f"ID для отслеживания: `{category}.{get_id}`", reply_markup=kb.exit_kb,
                         parse_mode=ParseMode.MARKDOWN_V2)


async def uncorrect_input(message):
    await message.answer("Некорректный ввод", reply_markup=kb.exit_kb)


@form_router.message()
async def echo(message: Message) -> None:
    if message.text.lower() in ['привет', 'hello', 'hi']:
        await message.answer(random.choice(['Пока', '...']))
    elif message.text.lower() in ['как дела', 'как дела?']:
        await message.answer(random.choice(['Никак', 'Отстань пж']))
    else:
        await message.answer(random.choice(['Я тебя не понимаю', 'Что?', '???', '...', 'Алоо ай донт андерстенд',
                                            'Неизвестная команда']), reply_markup=kb.exit_kb)
