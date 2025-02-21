from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, FSInputFile, PhotoSize
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from utils.models import AdminUsers, Users, Services, Category, PaymentsT, Stud, St_per
from utils.states import AdminStates
from datetime import datetime
from aiogram.types.input_file import BufferedInputFile
import csv
from utils.keyboards import (
    admin_menu_kb,
    categories_manage_kb,
    services_manage_kb,
    back_to_admin_kb,
    edit_service_kb, 
    edit_category_kb
)

admin_router = Router()

async def check_admin(user_id: int) -> bool:
    return Users.select().where(Users.user_id == user_id, Users.is_admin == 1).exists()

# Главное меню админки
@admin_router.callback_query(F.data == "admin")
async def admin_panel(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer("🚫 Доступ запрещен!")
    
    await callback.message.edit_text(
        "🛠️ Админ-панель:",
        reply_markup=admin_menu_kb()
    )

# Управление категориями
@admin_router.callback_query(F.data == "manage_categories")
async def manage_categories(callback: CallbackQuery):
    categories = Category.select()
    await callback.message.edit_text(
        "📂 Управление категориями:",
        reply_markup=categories_manage_kb(categories)
    )

@admin_router.callback_query(F.data == "add_category")
async def add_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.add_category_name)
    await callback.message.edit_text(
        "📝 Введите название новой категории:",
        reply_markup=back_to_admin_kb()
    )

@admin_router.message(AdminStates.add_category_name)
async def process_add_category_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminStates.add_category_photo)
    await message.answer("📸 Пришлите фото для категории или напишите 'Пропустить':")

@admin_router.message(AdminStates.add_category_photo)
async def process_add_category_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    
    if message.photo:
        data["image"] = message.photo[-1].file_id
    elif message.text and message.text.lower() == "пропустить":
        data["image"] = None
    
    Category.create(
        name=data["name"],
        sname=data.get("sname", data["name"][:15]),
        image=data.get("image")
    )
    
    await state.clear()
    await message.answer("✅ Категория добавлена!", reply_markup=admin_menu_kb())

# Управление услугами
@admin_router.callback_query(F.data == "manage_services")
async def manage_services(callback: CallbackQuery):
    services = Services.select().join(Category)
    await callback.message.edit_text(
        "💰 Управление тарифами:",
        reply_markup=services_manage_kb(services)
    )

# Добавление услуги (последовательно)
@admin_router.callback_query(F.data == "add_service")
async def add_service(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.add_service_name)
    await callback.message.edit_text(
        "📝 Введите название услуги:",
        reply_markup=back_to_admin_kb()
    )

@admin_router.message(AdminStates.add_service_name)
async def process_add_service_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminStates.add_service_price)
    await message.answer("📝 Введите цену услуги:")

# admin.py
@admin_router.message(AdminStates.add_service_price)
async def process_add_service_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        
        # Показываем список категорий для выбора
        categories = Category.select()
        builder = InlineKeyboardBuilder()
        for cat in categories:
            builder.button(text=cat.name, callback_data=f"select_cat_{cat.id}")
        builder.button(text="↩️ Отмена", callback_data="admin")
        builder.adjust(2)
        
        await state.set_state(AdminStates.add_service_category)
        await message.answer("📂 Выберите категорию:", reply_markup=builder.as_markup())
        
    except ValueError:
        await message.answer("❌ Цена должна быть числом. Попробуйте снова.")

@admin_router.callback_query(F.data.startswith("select_cat_"))
async def process_select_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[2])
    await state.update_data(category_id=category_id)
    await state.set_state(AdminStates.add_service_description)
    await callback.message.answer("📝 Введите описание услуги:")

@admin_router.message(AdminStates.add_service_description)
async def process_add_service_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AdminStates.add_service_photo)
    await message.answer("📸 Пришлите фото для услуги или напишите 'Пропустить':")

# admin.py
@admin_router.message(AdminStates.add_service_photo)
async def process_add_service_without_photo(message: Message, state: FSMContext):
    if message.photo:
        photo_id = message.photo[-1].file_id
        data = await state.get_data()
        data["image"] = photo_id
        
        Services.create(**data)
        await state.clear()
        await message.answer("✅ Услуга добавлена с фото!", reply_markup=admin_menu_kb())
    # Если пользователь отправил текст "Пропустить"
    elif message.text and message.text.lower() == "пропустить":
        data = await state.get_data()
        Services.create(**data)
        await state.clear()
        await message.answer("✅ Услуга добавлена без фото!", reply_markup=admin_menu_kb())

    

    

# Редактирование услуги
@admin_router.callback_query(F.data.startswith("edit_srv_"))
async def edit_service_start(callback: CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split("_")[2])
    service = Services.get_by_id(service_id)
    await state.update_data(service_id=service_id)
    await state.set_state(AdminStates.edit_service)
    await callback.message.edit_text(
        f"✏️ Редактирование услуги:\n\n"
        f"Название: {service.name}\n"
        f"Цена: {service.price}р\n"
        f"Категория: {service.category.name}\n"
        f"Описание: {service.description}\n\n"
        "Выберите действие:",
        reply_markup=edit_service_kb(service_id)
    )

@admin_router.callback_query(F.data.startswith("update_srv_"))
async def update_service_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split("_")[2]
    await state.update_data(field=field)
    await state.set_state(AdminStates.edit_service_value)
    await callback.message.edit_text(
        f"✏️ Введите новое значение для {field}:",
        reply_markup=back_to_admin_kb()
    )

@admin_router.message(AdminStates.edit_service_value)
async def process_update_service(message: Message, state: FSMContext):
    data = await state.get_data()
    service_id = data["service_id"]
    field = data["field"]
    service = Services.get_by_id(service_id)
    
    if field == "name":
        service.name = message.text
    elif field == "price":
        service.price = int(message.text)
    elif field == "category":
        service.category = Category.get_by_id(int(message.text))
    elif field == "description":
        service.description = message.text
    
    service.save()
    await state.clear()
    await message.answer("✅ Услуга обновлена!", reply_markup=admin_menu_kb())

@admin_router.callback_query(F.data.startswith("delete_srv_"))
async def delete_service(callback: CallbackQuery):
    service_id = int(callback.data.split("_")[2])
    service = Services.get_by_id(service_id)
    service.delete_instance()
    await callback.message.edit_text(
        "✅ Услуга удалена!",
        reply_markup=admin_menu_kb()
    )

# Экспорт данных в TXT
@admin_router.callback_query(F.data == "export_users_txt")
async def export_users_txt(callback: CallbackQuery):
    try:
        with open("users.txt", "w", encoding="utf-8") as file:
            users = Users.select()
            for user in users:
                file.write(f"Пользователь: {user.fullname}\n")
                file.write(f"Телефон: {user.phone_number}\n")
                file.write(f"Email: {user.email}\n")
                
                students = Stud.select().join(St_per).where(St_per.id_per == user.id)
                if students:
                    file.write("Дети:\n")
                    for student in students:
                        file.write(f" - {student.fullname}\n")
                file.write("\n" + "="*50 + "\n")
        
        await callback.message.answer_document(BufferedInputFile.from_file("users.txt", filename="users.txt"))
        await callback.answer("✅ Экспорт завершен!")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {str(e)}")

@admin_router.callback_query(F.data == "export_payments_txt")
async def export_payments_txt(callback: CallbackQuery):
    try:
        with open("payments.txt", "w", encoding="utf-8") as file:
            payments = PaymentsT.select()
            for p in payments:
                file.write(f"Платеж #{p.id}\n")
                file.write(f"Дата: {p.payment_date.strftime('%Y-%m-%d')}\n")
                file.write(f"Сумма: {p.price} руб.\n")
                file.write(f"Услуга: {p.service.name}\n")
                file.write(f"Пользователь: {p.user.fullname}\n")
                file.write("\n" + "-"*50 + "\n")
        
        await callback.message.answer_document(BufferedInputFile.from_file("payments.txt", filename="payments.txt"))
        await callback.answer("✅ Экспорт завершен!")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {str(e)}")

# Рассылка
@admin_router.callback_query(F.data == "broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.broadcast_message)
    await callback.message.edit_text(
        "📢 Введите сообщение для рассылки:",
        reply_markup=back_to_admin_kb()
    )

@admin_router.message(AdminStates.broadcast_message)
async def process_broadcast(message: Message, state: FSMContext):
    users = Users.select()
    success = 0
    failed = 0
    
    for user in users:
        try:
            await message.bot.send_message(
                chat_id=user.user_id,
                text=message.text
            )
            success += 1
        except:
            failed += 1
    
    await message.answer(
        f"✅ Рассылка завершена:\n"
        f"Доставлено: {success}\n"
        f"Не удалось: {failed}",
        reply_markup=admin_menu_kb()
    )
    await state.clear()

@admin_router.callback_query(F.data == "stats")
async def stats_menu(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для выбора периода статистики.
    """
    await state.set_state(AdminStates.stats_period)
    await callback.message.edit_text(
        "📊 Введите период для статистики в формате:\n"
        "ГГГГ-ММ-ДД ГГГГ-ММ-ДД\n"
        "Пример: 2024-01-01 2024-12-31",
        reply_markup=back_to_admin_kb()
    )

@admin_router.message(AdminStates.stats_period)
async def process_stats(message: Message, state: FSMContext):
    try:
        start_date_str, end_date_str = message.text.split()
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        payments = PaymentsT.select().where(
            (PaymentsT.payment_date >= start_date) &
            (PaymentsT.payment_date <= end_date)
        )
        
        total_amount = sum(p.price for p in payments)
        total_count = payments.count()
        
        await message.answer(
            f"📊 Статистика за период {start_date.date()} - {end_date.date()}:\n\n"
            f"💰 Общая сумма: {total_amount}р\n"
            f"📄 Количество платежей: {total_count}",
            reply_markup=admin_menu_kb()
        )
    except ValueError:
        await message.answer("❌ Неверный формат даты! Пример: 2024-01-01 2024-12-31")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        await state.clear()


@admin_router.callback_query(F.data == "export_data")
@admin_router.callback_query(F.data == "export_data")
async def export_data_menu(callback: CallbackQuery):
    """
    Обработчик для выбора типа данных для экспорта.
    """
    await callback.message.edit_text(
        "📁 Выберите данные для экспорта:",
        reply_markup=InlineKeyboardBuilder()
            .button(text="📄 Пользователи", callback_data="export_users")
            .button(text="💰 Платежи", callback_data="export_payments")
            .button(text="↩️ Назад", callback_data="admin")
            .adjust(1)
            .as_markup()
    )

@admin_router.callback_query(F.data == "export_users")
async def export_users(callback: CallbackQuery):
    """
    Обработчик для экспорта данных пользователей в CSV.
    """
    try:
        users = Users.select()
        with open("users.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "ФИО", "Телефон", "Email"])
            for user in users:
                writer.writerow([user.id, user.fullname, user.phone_number, user.email])
        
        # Отправляем файл пользователю
        await callback.message.answer_document(FSInputFile("users.csv"))
        await callback.answer("✅ Экспорт завершен!")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {str(e)}")

@admin_router.callback_query(F.data == "export_payments")
async def export_payments(callback: CallbackQuery):
    """
    Обработчик для экспорта данных платежей в CSV.
    """
    try:
        payments = PaymentsT.select()
        with open("payments.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Пользователь", "Услуга", "Цена", "Дата"])
            for payment in payments:
                writer.writerow([
                    payment.id,
                    payment.user.fullname,
                    payment.service.name,
                    payment.price,
                    payment.payment_date.strftime("%Y-%m-%d")
                ])
        
        # Отправляем файл пользователю
        await callback.message.answer_document(FSInputFile("payments.csv"))
        await callback.answer("✅ Экспорт завершен!")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {str(e)}")


@admin_router.callback_query(F.data == "manage_admins")
async def manage_admins(callback: CallbackQuery):
    admins = Users.select().where(Users.is_admin == 1)
    builder = InlineKeyboardBuilder()
    
    for admin in admins:
        user = Users.get(user_id=admin.user_id)
        builder.button(text=f"{user.fullname} ({admin.user_id})", 
                      callback_data=f"admin_info_{admin.user_id}")
    
    builder.button(text="➕ Добавить админа", callback_data="add_admin")
    builder.button(text="↩️ Назад", callback_data="admin")
    builder.adjust(1)
    
    await callback.message.edit_text(
        "Список администраторов:",
        reply_markup=builder.as_markup()
    )

@admin_router.callback_query(F.data.startswith("add_admin"))
async def add_admin_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.add_admin)
    await callback.message.edit_text(
        "Введите ID пользователя для назначения админом:",
        reply_markup=back_to_admin_kb()
    )

@admin_router.message(AdminStates.add_admin)
async def process_add_admin(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        AdminUsers.create(user_id=user_id)
        await message.answer("✅ Админ успешно добавлен!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    await state.clear()


@admin_router.callback_query(F.data.startswith("edit_cat_"))
async def edit_category_handler(callback: CallbackQuery, state: FSMContext):
    try:
        category_id = int(callback.data.split("_")[2])  # Исправлен индекс
        category = Category.get_by_id(category_id)
        await state.update_data(category_id=category_id)
        await state.set_state(AdminStates.edit_category)
        
        await callback.message.edit_text(
            f"✏️ Редактирование категории:\n\n"
            f"Название: {category.name}\n"
            f"Сокращенное название: {category.sname}\n\n"
            "Выберите действие:",
            reply_markup=edit_category_kb(category_id)  # Использование новой клавиатуры
        )
    except (IndexError, Category.DoesNotExist):
        await callback.answer("❌ Категория не найдена!")

@admin_router.callback_query(F.data.startswith("update_cat_name_"))
async def update_category_name_handler(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для изменения названия категории.
    """
    category_id = int(callback.data.split("_")[3])
    await state.update_data(category_id=category_id)
    await state.set_state(AdminStates.edit_category_name)
    await callback.message.edit_text(
        "✏️ Введите новое название категории:",
        reply_markup=back_to_admin_kb()
    )

@admin_router.message(AdminStates.edit_category_name)
async def process_update_category_name(message: Message, state: FSMContext):
    """
    Обработчик для сохранения нового названия категории.
    """
    data = await state.get_data()
    category_id = data["category_id"]
    category = Category.get_by_id(category_id)
    category.name = message.text
    category.save()
    
    await state.clear()
    await message.answer("✅ Название категории успешно изменено!", reply_markup=admin_menu_kb())

@admin_router.callback_query(F.data.startswith("update_cat_sname_"))
async def update_category_sname_handler(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для изменения сокращенного названия категории.
    """
    category_id = int(callback.data.split("_")[3])
    await state.update_data(category_id=category_id)
    await state.set_state(AdminStates.edit_category_sname)
    await callback.message.edit_text(
        "✏️ Введите новое сокращенное название категории:",
        reply_markup=back_to_admin_kb()
    )

@admin_router.message(AdminStates.edit_category_sname)
async def process_update_category_sname(message: Message, state: FSMContext):
    """
    Обработчик для сохранения нового сокращенного названия категории.
    """
    data = await state.get_data()
    category_id = data["category_id"]
    category = Category.get_by_id(category_id)
    category.sname = message.text
    category.save()
    
    await state.clear()
    await message.answer("✅ Сокращенное название категории успешно изменено!", reply_markup=admin_menu_kb())

@admin_router.callback_query(F.data.startswith("delete_cat_"))
async def delete_category_handler(callback: CallbackQuery):
    """
    Обработчик для удаления категории.
    """
    category_id = int(callback.data.split("_")[2])
    category = Category.get_by_id(category_id)
    category.delete_instance()
    
    await callback.message.edit_text(
        "✅ Категория успешно удалена!",
        reply_markup=admin_menu_kb()
    )


@admin_router.callback_query(F.data.startswith("update_cat_photo_"))
async def update_category_photo_handler(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[3])
    await state.update_data(category_id=category_id)
    await state.set_state(AdminStates.edit_category_photo)
    await callback.message.edit_text(
        "📸 Пришлите новое фото для категории или напишите 'Пропустить':",
        reply_markup=back_to_admin_kb()
    )

@admin_router.message(AdminStates.edit_category_photo)
async def process_update_category_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data["category_id"]
    category = Category.get_by_id(category_id)
    
    if message.photo:
        category.image = message.photo[-1].file_id
    elif message.text and message.text.lower() == "пропустить":
        category.image = None
    
    category.save()
    await state.clear()
    await message.answer("✅ Фото категории успешно обновлено!", reply_markup=admin_menu_kb())