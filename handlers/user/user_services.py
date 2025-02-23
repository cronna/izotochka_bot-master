from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from utils.keyboards import services_kb, categories_kb, user_show_service_kb, InlineKeyboardBuilder, main_menu, profile_kb
from utils.models import Services, Category, Stud, St_per,Users, StudentCourses
from utils.states import Registration, ProfileEditing
from datetime import datetime
from bot import bot

user_services_router = Router()


@user_services_router.callback_query(F.data == 'show_categories')
async def show_categories_handler(callback: CallbackQuery):
    categories = Category.select().where(Category.is_del == 0).order_by(Category.sortkey)
    try:
        await callback.message.edit_text(
            "<b>Выберите занятие:</b>",
            reply_markup=categories_kb(categories),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.delete()
        await callback.message.answer(
            "<b>Выберите занятие:</b>",
            reply_markup=categories_kb(categories),
            parse_mode="HTML"
        )
# Отправляет на количество занятий
@user_services_router.callback_query(F.data.startswith('show_category_info_'))
async def show_services_handler(callback: CallbackQuery):
    await callback.answer()
    try:
        category_id = int(callback.data.split('_')[3])
        category = Category.get_by_id(category_id)
        services = Services.select().where(
            (Services.category == category_id) &
            (Services.is_del == 0)
        ).order_by(+Services.sortkey)

        text = f"<b>{category.name}</b>\n\nВыберите услугу:"

        if category.image:
            await callback.message.answer_photo(
                category.image,
                caption=text,
                reply_markup=services_kb(services, 2)
            )
        else:
            await callback.message.answer(
                text,
                reply_markup=services_kb(services, 2),  # Передаем 2 для двух колонок
                parse_mode="HTML"
            )
    except (IndexError, ValueError, Category.DoesNotExist) as e:
        await callback.answer(f"❌ Ошибка: {str(e)}")
    
    

@user_services_router.callback_query(F.data.startswith('show_service_info'))
async def show_service_info_handler(callback: CallbackQuery):
    await callback.answer()
    try:
        service_id = int(callback.data.split()[1])
        service = Services.get(Services.id == service_id)
        user_id = callback.from_user.id
        
        text = f"""<b>{service.name}</b>
Цена: {service.price}₽

{service.description or ''}

Выберите ученика для записи:"""
        
        reply_markup = user_show_service_kb(service, user_id)
        current_has_photo = callback.message.photo is not None
        new_has_photo = service.image is not None

        if current_has_photo != new_has_photo:
            await callback.message.delete()
            if new_has_photo:
                await callback.message.answer_photo(
                    service.image,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
            else:
                await callback.message.answer(
                    text,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
        else:
            if new_has_photo:
                await callback.message.edit_media(
                    InputMediaPhoto(media=service.image, caption=text),
                    reply_markup=reply_markup
                )
            else:
                await callback.message.edit_text(
                    text,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
                
    except Exception as e:
        await callback.answer(f"⚠️ Ошибка: {str(e)}")


@user_services_router.message(Registration.input_stfullname)
async def input_fullname_handler(message: Message, state: FSMContext):
    if len(message.text.split()) != 3:
        return await message.edit_text('❌ Ошибка! Введи своё полное имя в формате: Фамилия Имя Отчество')
    fullname = ' '.join(list(map(lambda x: x.capitalize(), message.text.split())))
    data = await state.get_data()
    pp=data['servs']
  
    newst=Stud.create(fullname=fullname, id_crm=0)
   
    St_per.create(id_st= str(newst.id),id_per=str(Users.get(Users.user_id==message.from_user.id)))
    # St_per.create(id_st=7 ,id_per= 7)
       
    service: Services = Services.get_by_id(int(data['servs'])) 
    us=message.from_user.id
    text = f'''Вы выбрали
 <b>{service.category.name}</b> <b>{service.name}</b>
 <i>Стоимость: {service.price}₽</i>

 <b>Отлично, запомнил нового ученика, теперь вы можете выбрать его из списка ниже</b>'''
    
    await state.clear()
    await message.edit_text (text, reply_markup=user_show_service_kb(service, us), parse_mode="HTML")


@user_services_router.callback_query(F.data.startswith("add_to_course_"))
async def add_to_course_handler(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[3])
    user = Users.get(user_id=callback.from_user.id)
    
    # Получаем ВСЕХ учеников пользователя
    students = Stud.select().join(St_per).where(
        (St_per.id_per == user) &
        (Stud.is_del == False)
    )
    
    builder = InlineKeyboardBuilder()
    for student in students:
        builder.button(text=student.fullname, callback_data=f"select_student_{service_id}_{student.id}")
    
    builder.button(text="↩️ Назад", callback_data=f"show_service_info_{service_id}")
    await callback.message.edit_text(
        "👥 Выберите ученика для записи:",
        reply_markup=builder.adjust(1).as_markup()
    )

@user_services_router.callback_query(F.data.startswith("select_student_"))
async def process_add_to_course(callback: CallbackQuery):
    service_id = int(callback.data.split("_")[2])
    student_id = int(callback.data.split("_")[3])
    
    # Проверяем существование ученика
    if not Stud.select().where(Stud.id == student_id).exists():
        return await callback.edit_text("❌ Ученик не найден!")
    
    # Записываем на курс
    StudentCourses.create(
        student=student_id,
        service=service_id,
        start_date=datetime.now(),
        is_active=True
    )
    
    await callback.message.edit_text(
        "✅ Ученик успешно записан на занятие!",
        reply_mup=main_menu()
    )
    
# @user_services_router.callback_query(F.data.split()[0] == 'show_service_info')
# async def show_service_info_handler(callback: CallbackQuery):
#     service: Services = Services.get_by_id(int(callback.data.split()[1]))
#     text = f'''<b>{service.category.name}</b>
# <b>{service.name}</b>
# <i>Стоимость: {service.price}₽</i>'''
#     # Тут вывести учеников
#     await callback.message.edit_text(text, reply_markup=user_show_service_kb(service), parse_mode="HTML")


@user_services_router.callback_query(F.data == 'add_st')
async def add_student_start_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileEditing.add_student)
    await callback.message.edit_text(
        "Введите ФИО ученика в формате: Фамилия Имя Отчество",
        reply_markup=InlineKeyboardBuilder().button(text="↩️ Отмена", callback_data="profile").as_markup()
    )

@user_services_router.message(ProfileEditing.add_student)
async def add_student_finish_handler(message: Message, state: FSMContext):
    if len(message.text.split()) != 3:
        return await message.edit_text("❌ Неверный формат! Введите ФИО через пробел")
    
    fullname = ' '.join([word.capitalize() for word in message.text.split()])
    user = Users.get(Users.user_id == message.from_user.id)
    
    try:
        new_student = Stud.create(
            fullname=fullname,
            id_crm=0,
            is_del=False
        )
        St_per.create(id_st=new_student, id_per=user)
        
        await state.clear()
        try:
            await message.edit_text(
                f"✅ Ученик {fullname} успешно добавлен!",
                reply_markup=profile_kb()
            )
        except Exception:
            await message.answer(
                f"✅ Ученик {fullname} успешно добавлен!",
                reply_markup=profile_kb()
            )
        await message.delete()
        await bot.delete_message(message.from_user.id, message.message_id - 1)
    except Exception as e:
        await message.edit_text(f"❌ Ошибка: {str(e)}")

@user_services_router.callback_query(F.data.startswith('edit_st_fullname_'))
async def edit_student_fullname_start_handler(callback: CallbackQuery, state: FSMContext):
    student_id = int(callback.data.split('_')[3])
    await state.update_data(edit_student_id=student_id)
    await state.set_state(ProfileEditing.edit_student_name)
    await callback.message.edit_text(
        "Введите новое ФИО ученика:",
        reply_markup=InlineKeyboardBuilder().button(text="↩️ Отмена", callback_data="profile").as_markup()
    )

@user_services_router.message(ProfileEditing.edit_student_name)
async def edit_student_fullname_finish_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    student_id = data.get('edit_student_id')
    is_admin = Users.select().where(Users.user_id == message.from_user.id, Users.is_admin == 1).exists()
    
    if len(message.text.split()) != 3:
        return await message.answer("❌ Неверный формат! Введите ФИО через пробел")
    
    new_fullname = ' '.join([word.capitalize() for word in message.text.split()])
    
    try:
        student = Stud.get(Stud.id == student_id)
        student.fullname = new_fullname
        student.save()
        await message.answer(
            f"✅ ФИО ученика успешно изменено на: {new_fullname}",
            reply_markup=profile_kb()
        )
        await message.delete()
        await bot.delete_message(message.from_user.id, message.message_id - 1)
    except Stud.DoesNotExist:
        await message.edit_text("❌ Ученик не найден!", reply_markup=profile_kb())
    
    await state.clear()


@user_services_router.callback_query(F.data.startswith('addst '))
async def add_student_from_service_handler(callback: CallbackQuery, state: FSMContext):
    try:
        service_id = int(callback.data.split()[1])
        service = Services.get_by_id(service_id)
        
        # Сохраняем service_id в состоянии
        await state.update_data(service_id=service_id)
        await state.set_state(ProfileEditing.add_student_f)
        
        await callback.message.edit_text(
            "✏️ Введите ФИО нового ученика в формате: Фамилия Имя Отчество",
            reply_markup=InlineKeyboardBuilder()
                .button(text="↩️ Отмена", callback_data=f"show_service_info {service_id}")
                .as_markup()
        )
        
    except (IndexError, ValueError, Services.DoesNotExist):
        await callback.edit_text("❌ Ошибка при обработке услуги")

@user_services_router.message(ProfileEditing.add_student_f)
async def add_student_finish_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    service_id = data.get('service_id')
    user = Users.get(Users.user_id == message.from_user.id)
    
    # Валидация ФИО
    if len(message.text.split()) != 3:
        await message.delete()
        await bot.delete_message(message.from_user.id, message.message_id - 1)
        return await message.answer("❌ Неверный формат! Введите ФИО через пробел", 
                                       reply_markup=InlineKeyboardBuilder()
                .button(text="↩️ Отмена", callback_data=f"show_service_info {service_id}")
                .as_markup())
    
    fullname = ' '.join([word.capitalize() for word in message.text.split()])
    
    try:
        # Создание ученика
        new_student = Stud.create(
            fullname=fullname,
            id_crm=0,
            is_del=False
        )
        St_per.create(id_st=new_student, id_per=user)
        
        # Получаем обновленную услугу
        service = Services.get_by_id(service_id)
        
        # Возвращаемся к услуге
        await message.answer(
            f"✅ Ученик {fullname} добавлен!",
            reply_markup=user_show_service_kb(service, message.from_user.id)
        )
        await message.delete()
        await bot.delete_message(message.from_user.id, message.message_id - 1)
        await state.clear()
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}", reply_markup=user_show_service_kb(service, message.from_user.id))
        await message.delete()
        await bot.delete_message(message.from_user.id, message.message_id - 1)
        await state.clear()


@user_services_router.callback_query(F.data.startswith("back_to_"))
async def handle_back_buttons(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")