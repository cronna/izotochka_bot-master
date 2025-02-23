from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from utils.models import PaymentsT, Stud, Users, St_per
from utils.keyboards import history_kb, pagination_kb

history_router = Router()

@history_router.callback_query(F.data == "history")
async def show_history(callback: CallbackQuery):
    """
    Обработчик для показа списка учеников для выбора истории платежей.
    """
    user = Users.get(user_id=callback.from_user.id)
    students = Stud.select().join(St_per).where(St_per.id_per == user)
    await callback.message.edit_text(
        "Выберите ученика для просмотра истории платежей:",
        reply_markup=history_kb(students)
    )

@history_router.callback_query(F.data.startswith("hist_"))
async def show_student_history(callback: CallbackQuery):
    """
    Обработчик для показа истории платежей ученика.
    """
    try:
        student_id = int(callback.data.split("_")[1])
        student = Stud.get_by_id(student_id)  # Проверяем, существует ли ученик
        
        payments = PaymentsT.select().where(
            (PaymentsT.id_st == student_id) &
            (PaymentsT.finished == True)
        ).order_by(PaymentsT.payment_date.desc())
    
    # Группируем платежи по категориям
        grouped = {}
        for p in payments:
            key = f"{p.service.category.name}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(p)
        
        # Формируем текст сообщения
        text = f"История платежей для {student.fullname}:\n\n"
        for category, pays in grouped.items():
            text += f"<b>{category}</b>\n"
            for i, pay in enumerate(pays, 1):
                text += f"{i}. {pay.payment_date.strftime('%d.%m.%Y')} - {pay.price}р.\n"
            text += "\n"
        
        # Добавляем пагинацию
        await callback.message.edit_text(
            text,
            reply_markup=pagination_kb(1, len(payments)),
            parse_mode="HTML"
        )
    except Stud.DoesNotExist:
        await callback.edit_text("❌ Ученик не найден!")

@history_router.callback_query(F.data.startswith("page_"))
async def pagination_handler(callback: CallbackQuery):
    page = int(callback.data.split("_")[1])
    student_id = int(callback.data.split("_")[2])
    student = Stud.get_by_id(student_id)
    
    payments = PaymentsT.select().where(
        (PaymentsT.id_st == student_id) &
        (PaymentsT.finished == True)
    ).order_by(PaymentsT.payment_date.desc())
    
    ITEMS_PER_PAGE = 5
    total_pages = (len(payments) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start_idx = (page-1)*ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    
    text = f"История платежей для {student.fullname}:\n\n"
    for i, pay in enumerate(payments[start_idx:end_idx], start=start_idx+1):
        text += f"{i}. {pay.payment_date.strftime('%d.%m.%Y')} - {pay.price}р. ({pay.service.name})\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=pagination_kb(page, total_pages, student_id),
        parse_mode="HTML"
    )


@history_router.callback_query(F.data.startswith("back_to_"))
async def handle_back_buttons(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception as e:
        print(f"Ошибка при удалении сообщения: {e}")