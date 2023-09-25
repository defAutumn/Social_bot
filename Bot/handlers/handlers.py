from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import TransportForm, LandscapingGarbageForm, Form
from typing import Any, Dict
from ..db.models import PostTransport, PostLandscaping, PostGarbage
from sqlalchemy.ext.asyncio import AsyncSession
import kb
from sqlalchemy import select

form_router = Router()


# -----------------------------------------------------

categories = {
    'landscaping': ['Благоустройство', 'Введите локацию'],
    'public_transport': ['Общественный транспорт', 'Напишите номер маршрута'],
    'garbage': ['Мусор', 'Введите локацию']}

subcategories = {
    'minibus': 'Маршрутное такси',
    'tram': 'Трамвай',
    'trolleybus': 'Троллейбус',
    'bus': 'Автобус'
}


@form_router.message(Command("start"))
@form_router.message(F.text == "Меню")
@form_router.message(F.text == "Выйти в меню")
async def command_start(message: Message) -> None:
    await message.answer(
        "Добро пожаловать",
        reply_markup=kb.menu,
    )


@form_router.callback_query(F.data == "send_form")
async def process_category(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.category)
    await message.message.answer(
        "Выбери категорию",
        reply_markup=kb.categories_kb,
    )


@form_router.callback_query(F.data == "landscaping")
async def process_location(clbk: CallbackQuery, state: FSMContext) -> None:
    await choose(clbk)
    await process_inner(clbk, state)


@form_router.callback_query(F.data == "garbage")
async def process_location(clbk: CallbackQuery, state: FSMContext) -> None:
    await choose(clbk)
    await process_inner(clbk, state)


@form_router.message(LandscapingGarbageForm.location)
async def process_like_write_bots(message: Message, state: FSMContext) -> None:
    await state.update_data(location=message.text)
    await state.set_state(LandscapingGarbageForm.description)

    await message.answer(
        "Опишите проблему",
        reply_markup=kb.exit_kb,
    )


@form_router.message(LandscapingGarbageForm.description)
async def process_like_write_bots(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.update_data(description=message.text)
    await state.clear()
    await show_summary(message=message, data=data, session=session)


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
    await state.update_data(number=message.text)
    await state.set_state(TransportForm.description)
    await message.answer('Опиши проблему', reply_markup=kb.exit_kb)


@form_router.message(TransportForm.description)
async def process_photo(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(TransportForm.photo_id)
    await message.answer('Фото', reply_markup=kb.exit_kb)


@form_router.message(TransportForm.photo_id)
async def process_final(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.update_data(photo_id=message.text)
    await state.clear()
    await show_summary(message=message, data=data, session=session)


async def process_inner(clbk, state):
    await state.update_data(category=clbk.data)
    if clbk.data in ['landscaping', 'garbage']:
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
    await clbk.message.answer('Введи номер маршрута', reply_markup=kb.exit_kb)


async def show_summary(message: Message, data: Dict[str, Any], session: AsyncSession) -> None:
    category = data["category"]

    if category == 'public_transport':
        description = data['description']
        subcategory = data['subcategory']
        number = data['number']

        await session.merge(PostTransport(
            user_id=message.from_user.id,
            subcategory=subcategory,
            number=number,
            description=description,
            photo_id=0,
            status='Принято'
        ))
        await session.commit()

        result = (await session.execute(select(PostTransport).
                                        where(PostTransport.user_id == message.from_user.id))).all()
        get_id = result[-1][0].__dict__['post_id']
    elif category in ['landscaping', 'garbage']:
        location = data["location"]
        description = data['description']

        if category == 'landscaping':
            await session.merge(PostLandscaping(
                user_id=message.from_user.id,
                location=location,
                description=description,
                photo_id=0,
                status='Принято'
            ))
            await session.commit()

            result = (await session.execute(select(PostLandscaping)
                                            .where(PostLandscaping.user_id == message.from_user.id))).all()
            get_id = result[-1][0].__dict__['post_id']

        elif category == 'garbage':
            await session.merge(PostGarbage(
                user_id=message.from_user.id,
                location=location,
                description=description,
                photo_id=0,
                status='Принято'
            ))
            await session.commit()

            result = (await session.execute(select(PostGarbage)
                                            .where(PostGarbage.user_id == message.from_user.id))).all()
            get_id = result[-1][0].__dict__['post_id']

    await message.answer(f"Большое спасибо! Ваше обращение принято! :)")
    await message.answer(f"ID для отслеживания: {category}.{get_id}", reply_markup=kb.exit_kb)
