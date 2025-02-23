# from aiogram import F, Router
# from aiogram.types import Message
# from aiogram.fsm.context import FSMContext
# import phonenumbers

# import re


# from utils.states import Registration
# from utils.models import Users
# from utils.keyboards import main_menu

# student_router = Router()

# @student_router.message(Registration.input_stfullname)
# async def input_fullname_handler(message: Message, state: FSMContext):
#     if len(message.text.split()) != 3:
#         return await message.edit_text('❌ Ошибка! Введи своё полное ученика в формате: Фамилия Имя Отчество')
#     fullname = ' '.join(list(map(lambda x: x.capitalize(), message.text.split())))
#     await state.update_data(stfullname=fullname)
#     await state.set_state(Registration.input_mail)
#     await message.edit_text(f'''✅ Приятно познакомиться, {fullname}.
# Укажите Ваш адрес электронной почты, на его я буду присылать чеки после оплаты''')