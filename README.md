# Телеграм бот для удобной и быстрой отправки обращений

## Описание
На данный момент доступно 4 категории, по которым люди могут обращаться
(благоустройство, транспорт, мусор и свободная форма). Пользователь отправляет
описание, локацию, номер маршрута(транспорт), фотографию. Итогом заполнения всех
полей является отправка в базу данных и выдача пользователю ID обращения для 
дальнейшего отслеживания статуса. 

Список используемых технологий:
- Python
- Aiogram 3
- SQLAlchemy 2

## Особенности
- PostgreSQL полключен с помощью сервиса Railway
- Был арендован VPS сервер для круглосуточного функционирования бота

## Запуск
- Бот запущен и доступен по адресу https://t.me/NotSmeshnoBot