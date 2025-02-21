from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import phonenumbers
# from utils.models import db

import re


from utils.states import Registration
from utils.models import Users
from utils.keyboards import main_menu

registration_router = Router()


@registration_router.message(Registration.input_fullname)
async def input_fullname_handler(message: Message, state: FSMContext):
    if len(message.text.split()) != 3:
        return await message.answer('❌ Ошибка! Введи своё полное имя в формате: Фамилия Имя Отчество')
    fullname = ' '.join(list(map(lambda x: x.capitalize(), message.text.split())))
    await state.update_data(fullname=fullname)
    await state.set_state(Registration.input_mail)
    await message.answer(f'''✅ Приятно познакомиться, {fullname}.
Укажите Ваш адрес электронной почты, на его я буду присылать чеки после оплаты''')

@registration_router.message(Registration.input_mail)
async def input_mail_handler(message: Message, state: FSMContext):
    regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")
    if re.fullmatch(regex, message.text) is None:
        return await message.answer('❌ Ошибка! Проверьте адрес электронной почты')
    email = message.text
   
    await state.update_data(email=email)
   
    await state.set_state(Registration.input_number)
    await message.answer(f'''✅ Укажите Ваш номер телефона в формате: +79007773344''')


@registration_router.message(Registration.input_number)
async def input_number_handler(message: Message, state: FSMContext):
    
    try:
        phone = phonenumbers.parse(message.text, 'RU')
    except:
        return await message.answer('❌ Ошибка! Введён неверный номер телефона, попробуйте ещё раз')
    if not phonenumbers.is_valid_number(phone):
        return await message.answer('❌ Ошибка! Введён неверный номер телефона, попробуйте ещё раз')
    data = await state.get_data()
    print (data['email'])
    print (data['fullname'])
   
    Users.create(user_id=message.from_user.id,fullname=data['fullname'],
                 phone_number=phone.national_number,
                 username=message.from_user.username if message.from_user.username else 'None', 
                 email=data['email'], id_crm=0)
    await state.clear()
    await message.answer('''Отлично, теперь вы можете оплачивать услуги нашей студии.
Нажмите кнопку ниже и выберите занятие.''',
                         reply_markup=main_menu())
