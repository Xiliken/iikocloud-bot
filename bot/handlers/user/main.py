from pprint import pprint

from aiogram.fsm.state import default_state
from aiogram.types import *
from aiogram import Router, F, Bot
from aiogram.filters import *
from aiogram.utils.formatting import Text
from bot.database.connect import DBManager
from bot.keyboards import auth_kb
from bot.keyboards.cabinet import cabinet_main_kb
from bot.keyboards.inline import chat_inline_kb

router: Router = Router()
db = DBManager()


# Обработчик команды "/start"
@router.message(CommandStart(), StateFilter(default_state))
async def __start(msg: Message) -> None:
    bot: Bot = msg.bot
    user_id = msg.from_user.id
    user = msg.from_user

    # Регистрация пользователя
    if not db.user_exists(user_id):
        # Делаем регистрацию через IikoCloud и добавляем пользователя в БД
        db.add_user(user_id, msg.from_user.username)
        print(
            f"Пользователь {user.first_name} {user.last_name if user.last_name is not None else ''} (id: {user_id}) был добавлен в базу данных!")
        await msg.answer(f"Привет! Я чат-тот стрит фуд ресторана <b><a href='https://doners-club.ru'>Донерс</a></b>.\n"
                         "Со мной тебя ждут скидки и специальные цены на продукцию, кэшбэк с каждой покупки, бонусы за отзывы и оценку заказов.\n\n"
                         f"Авторизуйся 1 раз и получай все преимущества \"DonersClub\" 😎",
                         parse_mode='HTML', disable_web_page_preview=True, reply_markup=auth_kb()
                         )

    elif db.user_exists(user_id):
        await msg.answer(f"С возвращением, <b>{user.first_name}</b>\n"
                         f"✅ Вы уже авторизованы в системе!\n"
                         f"Продолжайте работу с ботом 😄",
                         reply_markup=cabinet_main_kb(), parse_mode='HTML')


# # Обработчик кнопки и команды "Регистрация"
# @router.message(Command(commands=['reg', 'register']))
# @router.message(F.text == '🔐 Регистрация')
# async def registration_handler_stage1(msg: Message) -> None:
#     await msg.answer("Пожалуйста, выберите способ регистрации.", reply_markup=register_kb())
#
#
# # Обработчик кнопки и команды "Авторизация"
# @router.message(Command(commands=['login', 'auth']))
# @router.message(F.text == '🔑 Авторизация')
# async def login_handler(msg: Message) -> None:
#     await msg.answer('Пожалуйста, введите номер телефона для авторизации')
#     pass


# Обработчик кнопки и команды "Меню"
@router.message(F.text == 'Меню')
async def menu_handler(message: Message):
    pass


# Обработчик кнопки и команды "Чат"
@router.message(F.text == 'Чат')
@router.message(Command(commands=['chat']))
async def chat_handler(msg: Message) -> None:
    await msg.answer('Нажми на кнопку и напиши свой вопрос', reply_markup=chat_inline_kb())


# Обработчик остальных сообщений
# TODO: Нужно сделать так, чтобы он всегда шел последним хендлером, тогда только вернуть его в работу
# @router.message()
# async def send_message(msg: Message) -> None:
#     await msg.answer(f"Простите, но мой интеллект еще не настолько умен, чтобы общаться с вами на любые темы! ☹️\n"
#                      f"Пожалуйста, для общения со мной, используйте команды или меню ниже! 🤗")
