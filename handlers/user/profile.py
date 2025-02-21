from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from utils.models import Users, Stud, St_per, StudentCourses
from utils.states import ProfileEditing
from utils.keyboards import (
    profile_kb, 
    edit_profile_kb, 
    edit_student_kb, 
    manage_students_kb,
    back_to_profile_kb,
    InlineKeyboardBuilder
)
import phonenumbers
import re
from datetime import datetime

profile_router = Router()

@profile_router.callback_query(F.data == "edit_fullname")
async def start_edit_fullname(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileEditing.edit_fullname)
    await callback.message.edit_text(
        "✏️ Введите новое ФИО:",
        reply_markup=back_to_profile_kb()
    )

@profile_router.message(ProfileEditing.edit_fullname)
async def process_edit_fullname(message: Message, state: FSMContext):
    if len(message.text.split()) != 3:
        return await message.answer("❌ Неверный формат! Пример: Иванов Иван Иванович")
    
    user = Users.get(user_id=message.from_user.id)
    user.fullname = ' '.join([word.capitalize() for word in message.text.split()])
    user.save()
    
    await state.clear()
    await message.answer("✅ ФИО успешно обновлено!", reply_markup=profile_kb())

@profile_router.callback_query(F.data == "edit_phone")
async def start_edit_phone(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileEditing.edit_phone)
    await callback.message.edit_text(
        "📱 Введите новый номер телефона:",
        reply_markup=back_to_profile_kb()
    )

@profile_router.message(ProfileEditing.edit_phone)
async def process_edit_phone(message: Message, state: FSMContext):
    try:
        parsed = phonenumbers.parse(message.text, "RU")
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError
    except:
        return await message.answer("❌ Неверный формат номера! Пример: +79161234567")
    
    user = Users.get(user_id=message.from_user.id)
    user.phone_number = phonenumbers.format_number(
        parsed, 
        phonenumbers.PhoneNumberFormat.E164
    )
    user.save()
    
    await state.clear()
    await message.answer("✅ Телефон успешно обновлен!", reply_markup=profile_kb())

@profile_router.callback_query(F.data == "edit_email")
async def start_edit_email(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileEditing.edit_email)
    await callback.message.edit_text(
        "📧 Введите новый email:",
        reply_markup=back_to_profile_kb()
    )

@profile_router.message(ProfileEditing.edit_email)
async def process_edit_email(message: Message, state: FSMContext):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", message.text):
        return await message.answer("❌ Неверный формат email! Пример: user@example.com")
    
    user = Users.get(user_id=message.from_user.id)
    user.email = message.text
    user.save()
    
    await state.clear()
    await message.answer("✅ Email успешно обновлен!", reply_markup=profile_kb())

@profile_router.callback_query(F.data.startswith("delete_student_"))
async def delete_student(callback: CallbackQuery):
    student_id = int(callback.data.split("_")[2])
    student = Stud.get_by_id(student_id)
    student.is_del = True
    student.save()
    await callback.message.edit_text(
        "✅ Ученик помечен как удаленный",
        reply_markup=profile_kb()
    )

@profile_router.callback_query(F.data == 'profile')
async def show_profile(callback: CallbackQuery):
    """
    Обработчик для показа профиля пользователя.
    """
    user = Users.get(user_id=callback.from_user.id)
    students = Stud.select().join(St_per).where(St_per.id_per == user)
    
    text = f"""<b>Профиль</b>
👤 ФИО: {user.fullname}
📱 Телефон: {user.phone_number}
📧 Email: {user.email}

<b>Ученики:</b>\n"""
    
    for student in students:
        courses = StudentCourses.select().where(StudentCourses.student == student)
        text += f"\n🎓 {student.fullname}"
        if student.is_del:
            text += " (удален)"
        text += "\nЗанятия: "
        text += ", ".join([c.service.name for c in courses]) + "\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=profile_kb(),
        parse_mode="HTML"
    )

@profile_router.callback_query(F.data == 'edit_profile')
async def edit_profile_start(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для начала редактирования профиля.
    """
    await state.set_state(ProfileEditing.choose_field)
    await callback.message.edit_text(
        "Что вы хотите изменить?",
        reply_markup=edit_profile_kb()
    )

@profile_router.callback_query(F.data == 'manage_students')
async def manage_students(callback: CallbackQuery):
    """
    Обработчик для управления учениками.
    """
    user = Users.get(user_id=callback.from_user.id)
    students = Stud.select().join(St_per).where(St_per.id_per == user)
    await callback.message.edit_text(
        "Выберите ученика для редактирования:",
        reply_markup=manage_students_kb(students)
    )

@profile_router.callback_query(F.data.startswith('edit_student_'))
async def edit_student(callback: CallbackQuery):
    """
    Обработчик для редактирования данных ученика.
    """
    student_id = int(callback.data.split('_')[2])
    await callback.message.edit_text(
        "Выберите действие:",
        reply_markup=edit_student_kb(student_id)
    )


@profile_router.callback_query(F.data == "add_student")
async def add_student_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileEditing.add_student)
    await callback.message.edit_text(
        "👶 Введите ФИО нового ученика:",
        reply_markup=InlineKeyboardBuilder()
            .button(text="↩️ Отмена", callback_data="profile")
            .as_markup()
    )

@profile_router.message(ProfileEditing.add_student)
async def process_add_student(message: Message, state: FSMContext):
    try:
        user = Users.get(user_id=message.from_user.id)
        student = Stud.create(
            fullname=' '.join([word.capitalize() for word in message.text.split()]),
            is_del=False
        )
        St_per.create(id_st=student, id_per=user)
        await state.clear()
        await message.answer("✅ Ученик успешно добавлен!", reply_markup=profile_kb())
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@profile_router.callback_query(F.data.startswith("edit_student_"))
async def edit_student_handler(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для редактирования ученика.
    """
    student_id = int(callback.data.split("_")[2])
    await state.update_data(student_id=student_id)
    await state.set_state(ProfileEditing.edit_student_name)
    await callback.message.edit_text(
        "✏️ Введите новое ФИО ученика:",
        reply_markup=back_to_profile_kb()
    )

@profile_router.message(ProfileEditing.edit_student_name)
async def process_edit_student(message: Message, state: FSMContext):
    """
    Обработчик для сохранения изменений ФИО ученика.
    """
    data = await state.get_data()
    student_id = data["student_id"]
    student = Stud.get_by_id(student_id)
    student.fullname = ' '.join([word.capitalize() for word in message.text.split()])
    student.save()
    
    await state.clear()
    await message.answer("✅ ФИО ученика успешно изменено!", reply_markup=profile_kb())

@profile_router.callback_query(F.data.startswith("delete_student_"))
async def delete_student_handler(callback: CallbackQuery):
    """
    Обработчик для удаления ученика.
    """
    student_id = int(callback.data.split("_")[2])
    student = Stud.get_by_id(student_id)
    student.is_del = True
    student.save()
    
    await callback.message.edit_text(
        "✅ Ученик помечен как удаленный.",
        reply_markup=profile_kb()
    )


@profile_router.callback_query(F.data.startswith("view_courses_"))
async def view_student_courses(callback: CallbackQuery):
    """
    Обработчик для просмотра занятий ученика.
    """
    student_id = int(callback.data.split("_")[2])
    student = Stud.get_by_id(student_id)
    courses = StudentCourses.select().where(
        (StudentCourses.student == student) &
        (StudentCourses.is_active == True)
    )
    
    text = f"🎓 Занятия ученика {student.fullname}:\n\n"
    for course in courses:
        text += f"- {course.service.name} ({course.start_date} - {course.end_date or 'по настоящее время'})\n"
    
    await callback.message.edit_text(
        text,
        reply_mup=back_to_profile_kb()
    )


@profile_router.callback_query(F.data.startswith("add_course_"))
async def add_course_handler(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для добавления занятия ученику.
    """
    student_id = int(callback.data.split("_")[2])
    await state.update_data(student_id=student_id)
    await state.set_state(ProfileEditing.add_course)
    await callback.message.edit_text(
        "📅 Введите данные занятия в формате:\n"
        "ID услуги|Дата начала (ГГГГ-ММ-ДД)|Дата окончания (ГГГГ-ММ-ДД)\n"
        "Пример: 1|2024-01-01|2024-12-31",
        reply_markup=back_to_profile_kb()
    )

@profile_router.message(ProfileEditing.add_course)
async def process_add_course(message: Message, state: FSMContext):
    """
    Обработчик для сохранения нового занятия.
    """
    data = await state.get_data()
    student_id = data["student_id"]
    
    try:
        service_id, start_date_str, end_date_str = message.text.split("|")
        start_date = datetime.strptime(start_date_str.strip(), "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str.strip(), "%Y-%m-%d") if end_date_str.strip() else None
        
        StudentCourses.create(
            student=student_id,
            service=service_id.strip(),
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        
        await message.answer("✅ Занятие успешно добавлено!", reply_markup=profile_kb())
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    await state.clear()


@profile_router.callback_query(F.data.startswith("delete_course_"))
async def delete_course_handler(callback: CallbackQuery):
    """
    Обработчик для удаления занятия.
    """
    course_id = int(callback.data.split("_")[2])
    course = StudentCourses.get_by_id(course_id)
    course.is_active = False
    course.save()
    
    await callback.message.edit_text(
        "✅ Занятие успешно удалено!",
        reply_markup=profile_kb()
    )