"""Module using to handle start message or show main menu from back callbacks"""
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.models import Users, AdminUsers
from utils.states import Registration
from utils.keyboards import main_menu

start_router = Router()


@start_router.message(Command('start'))
@start_router.callback_query(F.data == 'start')
async def start_handler(event: Message | CallbackQuery, state: FSMContext = None):
    """
    Обработчик для команды /start и возврата в главное меню.
    """
    await state.clear()
    user = Users.get_or_none(Users.user_id == event.from_user.id)

    registration_text = f'''👋 Здравствуйте, {event.from_user.full_name}!

Я, Пикассо, бот студии Изоточка 👨‍🎨, помогаю оплатить занятия и мастер-классы!
Представьтесь, пожалуйста, я Вас зарегистрирую.
Укажите полное имя в формате: Фамилия Имя Отчество.'''

    start_text = f'''👋 Здравствуйте, {event.from_user.full_name}!
    
Я, Пикассо, бот студии Изоточка 👨‍🎨, помогаю оплатить занятия и мастер-классы!'''

    if not user:
        print("Не зарегистрирован")
        await event.answer(registration_text, parse_mode="HTML")
        await state.set_state(Registration.input_fullname)
    else:
        # Проверяем, является ли пользователь админом
        is_admin = Users.select().where(Users.user_id == event.from_user.id, Users.is_admin == 1).exists()
        
        if isinstance(event, Message):
            await event.delete()
            await event.answer(
                start_text,
                reply_markup=main_menu(is_admin),
                parse_mode="HTML"
            )
        else:
            await event.message.answer(
                start_text,
                reply_markup=main_menu(is_admin),
                parse_mode="HTML"
            )