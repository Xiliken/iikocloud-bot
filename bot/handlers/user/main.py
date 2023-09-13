from pprint import pprint

from aiogram.fsm.state import default_state
from aiogram.types import Message, ContentType, Contact
from aiogram import Router, F, Bot
from aiogram.filters import CommandObject, Command, CommandStart, StateFilter
from aiogram.utils.formatting import Text
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.connect import DBManager
from bot.database.methods.user_exists import user_exists
from bot.database.models.User import User
from bot.keyboards import auth_kb
from bot.keyboards.cabinet import cabinet_main_kb
from bot.keyboards.inline import chat_inline_kb, contacts_ikb

router: Router = Router()


# db = DBManager()


# Обработчик команды "/start"
@router.message(CommandStart(), StateFilter(default_state))
async def __start(msg: Message, session: AsyncSession) -> None:
    bot: Bot = msg.bot
    user_id = msg.from_user.id
    user = msg.from_user

    sql = await session.execute(select(User).where(User.user_id == user_id))

    # Если такой пользователь уже существует
    if sql.scalar():
        await msg.answer(f"С возвращением, <b>{user.first_name}</b>\n"
                         f"✅ Вы уже авторизованы в системе!\n"
                         f"Продолжайте работу с ботом 😄",
                         reply_markup=cabinet_main_kb(), parse_mode='HTML')
    else:
        # Добавление нового пользователя
        # await session.merge(User(user_id=user_id, is_admin=False))
        await msg.answer(f"Привет! Я чат-бот стрит фуд ресторана <b><a href='https://doners-club.ru'>Донерс</a></b>.\n"
                         "Со мной тебя ждут скидки и специальные цены на продукцию, кэшбэк с каждой покупки, бонусы за отзывы и оценку заказов.\n\n"
                         f"Авторизуйся 1 раз и получай все преимущества \"DonersClub\" 😎",
                         parse_mode='HTML', disable_web_page_preview=True, reply_markup=auth_kb()
                         )

    await session.commit()


# Обработчик кнопки и команды "Меню"
@router.message(F.text == 'Меню')
async def menu_handler(message: Message):
    pass


# Обработчик кнопки и команды "Чат"
@router.message(F.text == 'Чат')
@router.message(Command(commands=['chat']))
async def chat_handler(msg: Message) -> None:
    await msg.answer('Нажми на кнопку и напиши свой вопрос', reply_markup=chat_inline_kb())


# Обработчик кнопки и команды "Контакты"
@router.message(F.text == 'Контакты')
@router.message(Command(commands=['contacts', 'contact']))
async def chat_handler(msg: Message) -> None:
    await msg.answer('Выбери ресторан:', reply_markup=contacts_ikb())

# Обработчик остальных сообщений
# TODO: Нужно сделать так, чтобы он всегда шел последним хендлером, тогда только вернуть его в работу
# @router.message()
# async def send_message(msg: Message) -> None:
#     await msg.answer(f"Простите, но мой интеллект еще не настолько умен, чтобы общаться с вами на любые темы! ☹️\n"
#                      f"Пожалуйста, для общения со мной, используйте команды или меню ниже! 🤗")
