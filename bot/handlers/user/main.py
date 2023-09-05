from pprint import pprint

from aiogram.types import *
from aiogram import Router, F, Bot, Dispatcher
from aiogram.filters import *
from pyiikocloudapi import IikoTransport
from tqdm import tqdm

from bot.database.connect import DBManager
from bot.keyboards import main_kb, auth_kb
from bot.keyboards.cabinet import cabinet_main_kb
from bot.keyboards.reply import register_kb
from bot.mics.helpers.Config import Config
from bot.mics.iikoapi import get_organizations_ids

router = Router()
db = DBManager()
dp = Dispatcher()

@router.message(CommandStart())
async def __start(msg: Message) -> None:
    bot: Bot = msg.bot
    user_id = msg.from_user.id
    user = msg.from_user


    # Регистрация пользователя
    if not db.user_exists(user_id):
        # Делаем регистрацию через IikoCloud и добавляем пользователя в БД
        db.add_user(user_id, msg.from_user.username)
        print(f"Пользователь {user.first_name} {user.last_name if user.last_name is not None else ''} (id: {user_id}) был добавлен в базу данных!")
        await msg.answer(f"Добро пожаловать, <b>{user.first_name}</b>!\n"
                         "Это официальный бот компании <a href='https://doners-club.ru/'>Домерс</a>\n"
                         f"Для дальнейшей работы с ботом, пожалуйста, войдите или создайте аккаунт Донерс!",
                         parse_mode='HTML', disable_web_page_preview=True, reply_markup=auth_kb()
                         )

    elif db.user_exists(user_id):
        await msg.answer(f"С возвращением, <b>{user.first_name}</b>\n"
                         f"✅ Вы уже авторизованы в системе!\n"
                         f"Продолжайте работу с ботом 😄",
                         reply_markup=cabinet_main_kb(), parse_mode='HTML')


@router.message(Command(commands=['reg', 'register']))
@router.message(F.text == '🔐 Регистрация')
async def registration_handler_stage1(msg: Message) -> None:
    await msg.answer("Пожалуйста, выберите способ регистрации.", reply_markup=register_kb())


@router.message(Command(commands=['login', 'auth']))
@router.message(F.text == '🔑 Авторизация')
async def login_handler(msg: Message) -> None:
    await msg.answer('Пожалуйста, введите номер телефона для авторизации')
    pass


@router.message()
async def send_message(msg: Message) -> None:
    await msg.answer(f"Простите, но мой интеллект еще не настолько умен, чтобы общаться с вами на любые темы! ☹️\n"
                     f"Пожалуйста, для общения со мной, используйте команды или меню ниже! 🤗")

