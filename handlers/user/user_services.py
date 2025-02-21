from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from utils.keyboards import services_kb, categories_kb, user_show_service_kb, InlineKeyboardBuilder, main_menu
from utils.models import Services, Category, Stud, St_per,Users, StudentCourses
from utils.states import Registration
from datetime import datetime

user_services_router = Router()


@user_services_router.callback_query(F.data == 'show_categories')
async def show_categories_handler(callback: CallbackQuery):
    categories = Category.select().where(Category.is_del == 0).order_by(Category.sortkey)
    

    text = f"<b>Выберите занятие: </b>"
    await callback.message.answer(
        text,
        reply_markup=categories_kb(categories),
        parse_mode="HTML"
    )

# Отправляет на количество занятий
@user_services_router.callback_query(F.data.startswith('show_category_info_'))
async def show_services_handler(callback: CallbackQuery):
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
                reply_markup=services_kb(services, 2),  # Передаем 2 для двух колонок
                parse_mode="HTML"
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
    try:
        # Разделяем данные и проверяем, что их достаточно
        data_parts = callback.data.split()
        if len(data_parts) < 2:
            await callback.answer("❌ Ошибка: некорректные данные.")
            return
        
        # Получаем ID услуги
        service_id = int(data_parts[1])
        service = Services.get(Services.id == service_id)
        user_id = callback.from_user.id  # Получаем ID пользователя
        
        # Формируем текст сообщения
        text = f"""<b>{service.name}</b>
Цена: {service.price}₽
{service.description or ''}"""

        # Отправляем сообщение с фото или текстом
        if service.image:
            await callback.message.answer_photo(
                service.image,
                text,
                reply_markup=user_show_service_kb(service, user_id),
                parse_mode="HTML"
            )
        else:
            await callback.message.answer(
                text,
                reply_markup=user_show_service_kb(service, user_id),
                parse_mode="HTML"
            )
    
    except Services.DoesNotExist:
        await callback.answer("❌ Услуга не найдена.")
    except ValueError:
        await callback.answer("❌ Некорректный ID услуги.")
    except Exception as e:
        await callback.answer(f"⚠️ Произошла ошибка: {str(e)}")


@user_services_router.message(Registration.input_stfullname)
async def input_fullname_handler(message: Message, state: FSMContext):
    if len(message.text.split()) != 3:
        return await message.answer('❌ Ошибка! Введи своё полное имя в формате: Фамилия Имя Отчество')
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
    await message.answer (text, reply_markup=user_show_service_kb(service, us), parse_mode="HTML")


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
        return await callback.answer("❌ Ученик не найден!")
    
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



print('hello world')



