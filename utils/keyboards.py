from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from utils.models import Services, Category,Users, St_per, Stud
from utils.states import Registration
from aiogram.types import InlineKeyboardButton, WebAppInfo
from yookassa import  Payment
from aiogram.types import CallbackQuery



def back_btn(callback):
    return InlineKeyboardBuilder().button(text='↩️ Назад', callback_data=callback).as_markup()


# utils/keyboards.py
def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='🎓 Занятия', callback_data='show_categories')
    builder.button(text='👤 Профиль', callback_data='profile')
    
    if is_admin:
        builder.button(text='🛠️ Админка', callback_data='admin')  # Только для админов
        
    builder.button(text='📜 История платежей', callback_data='history')
    return builder.adjust(1).as_markup()


def add_stud() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Добавить ученика', callback_data='add_st')
    builder.button(text='Выбрать занятие', callback_data='show_categories')
    return builder.as_markup()

def categories_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category.sname, callback_data=f'show_category_info_{category.id}')
    builder.button(text='↩️ Назад', callback_data='start')
    return builder.adjust(2).as_markup()


def services_kb(services: list[Services], columns: int = 2) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    for service in services:
        builder.button(text=f'{service.name} - {service.price}р', callback_data=f'show_service_info {service.id}')
    
    builder.adjust(columns)  # Используем переданное значение или значение по умолчанию (2)
    builder.row(InlineKeyboardButton(text='↩️ Назад', callback_data='back_to_show_categories'))
    return builder.as_markup()


# def user_show_service_kb(service: Services) -> InlineKeyboardMarkup:
#     builder = InlineKeyboardBuilder()
#     builder.button(text='🛒 Оплатить', callback_data=f'buy {service.id}')
#     builder.button(text='↩️ Назад', callback_data='start')
#     return builder.adjust(1).as_markup()

def user_show_service_kb(service: Services, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    user = Users.get_or_none(Users.user_id == user_id)
    
    if user:
        st_per = St_per.select().where(St_per.id_per == user.id)
        for stp in st_per:
            stud = Stud.get_or_none(Stud.id == stp.id_st)
            if stud and not stud.is_del:
                builder.button(text=stud.fullname, callback_data=f'buy {service.id} {stud.id}')
    
    builder.button(text='➕ Добавить ученика', callback_data=f'addst {service.id}')
    builder.button(text='↩️ Назад', callback_data='back_to_start')
    return builder.adjust(2).as_markup()


# def user_show_service_kb(service: Services) -> InlineKeyboardMarkup:
#     builder = InlineKeyboardBuilder()
#     builder.button(text='🛒 Оплатить', callback_data=f'buy {service.id}')
#     builder.button(text='↩️ Назад', callback_data='start')
#     return builder.adjust(1).as_markup()

def user_show_pay_kb(payment1: Payment) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='🛒 Ссылка для оплаты', callback_data='conf', url=payment1.confirmation.confirmation_url)
    builder.button(text='↩️ Назад', callback_data='start')
    return builder.adjust(1).as_markup()

 
def history_kb(students: list[Stud]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for student in students:
        text = student.fullname
        if student.is_del:
            text += " (удален)"
        builder.button(text=text, callback_data=f'hist_{student.id}')
    builder.button(text='↩️ Назад', callback_data='start')
    return builder.adjust(1).as_markup()

def profile_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='✏️ Изменить данные', callback_data='edit_profile')
    builder.button(text='👨🎓 Ученики и занятия', callback_data='student_courses')
    builder.button(text='📜 История платежей', callback_data='history')
    builder.button(text='↩️ На главную', callback_data='start')
    return builder.adjust(1).as_markup()

def edit_profile_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ ФИО", callback_data="edit_fullname")
    builder.button(text="📱 Телефон", callback_data="edit_phone")
    builder.button(text="📧 Email", callback_data="edit_email")
    builder.button(text="↩️ Назад", callback_data="profile")
    return builder.adjust(2).as_markup()

def admin_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='📦 Управление категориями', callback_data='manage_categories')
    builder.button(text='💰 Управление тарифами', callback_data='manage_services')
    builder.button(text='📊 Статистика', callback_data='stats')
    builder.button(text='📁 Экспорт данных', callback_data='export_data')
    builder.button(text='📨Рассылка', callback_data='broadcast')
    builder.button(text='👨‍🦰Админы', callback_data='manage_admins')
    builder.button(text='↩️ На главную', callback_data='start')
    return builder.adjust(1).as_markup()


def pagination_kb(current_page: int, total_pages: int, prefix: str = "page_") -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для пагинации.
    
    :param current_page: Текущая страница
    :param total_pages: Общее количество страниц
    :param prefix: Префикс для callback_data
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопка "Назад"
    if current_page > 1:
        builder.button(text="⬅️ Назад", callback_data=f"{prefix}{current_page - 1}")
    
    # Текущая страница
    builder.button(text=f"{current_page}/{total_pages}", callback_data="current_page")
    
    # Кнопка "Вперед"
    if current_page < total_pages:
        builder.button(text="Вперед ➡️", callback_data=f"{prefix}{current_page + 1}")
    
    # Кнопка "На главную"
    builder.button(text="↩️ На главную", callback_data="start")
    
    return builder.adjust(2, 1).as_markup()

def history_kb(students: list[Stud]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора ученика для просмотра истории платежей.
    
    :param students: Список учеников
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    for student in students:
        text = student.fullname
        if student.is_del:
            text += " (удален)"
        builder.button(text=text, callback_data=f"hist_{student.id}")
    builder.button(text="↩️ Назад", callback_data="start")
    return builder.adjust(1).as_markup()

def edit_student_kb(student_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для редактирования данных ученика.
    
    :param student_id: ID ученика
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить ФИО", callback_data=f"edit_st_fullname_{student_id}")
    builder.button(text="🗑️ Удалить ученика", callback_data=f"delete_student_{student_id}")
    builder.button(text="↩️ Назад", callback_data="profile")
    return builder.adjust(1).as_markup()

def profile_kb() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для управления профилем.
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить профиль", callback_data="edit_profile")
    builder.button(text="👨🎓 Управление учениками", callback_data="manage_students")
    builder.button(text="↩️ Назад", callback_data="start")
    return builder.adjust(1).as_markup()

def manage_students_kb(students: list[Stud]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for student in students:
        text = student.fullname
        if student.is_del:
            text += " (удален)"
        builder.button(text=text, callback_data=f"edit_student_{student.id}")
    builder.button(text="➕ Добавить ученика", callback_data="add_student")
    builder.button(text="↩️ Назад", callback_data="profile")
    return builder.adjust(1).as_markup()



def back_to_profile_kb():
    return InlineKeyboardBuilder().button(text="↩️ Назад", callback_data="profile").as_markup()

def back_to_admin_kb():
    return InlineKeyboardBuilder().button(text="↩️ Назад", callback_data="admin").as_markup()

def categories_manage_kb(categories: list[Category]):
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=f"{cat.name} ({cat.id})", callback_data=f"edit_cat_{cat.id}")
    builder.button(text="➕ Добавить", callback_data="add_category")
    builder.button(text="↩️ Назад", callback_data="admin")
    return builder.adjust(1).as_markup()

def edit_category_kb(category_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для редактирования категории с добавлением кнопки изменения фото
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить название", callback_data=f"update_cat_name_{category_id}")
    builder.button(text="📝 Изменить сокращение", callback_data=f"update_cat_sname_{category_id}")
    builder.button(text="🖼️ Изменить фото", callback_data=f"update_cat_photo_{category_id}")
    builder.button(text="🗑️ Удалить категорию", callback_data=f"delete_cat_{category_id}")
    builder.button(text="↩️ Назад", callback_data="manage_categories")
    return builder.adjust(1).as_markup()

def services_manage_kb(services: list[Services]):
    builder = InlineKeyboardBuilder()
    for srv in services:
        builder.button(text=f"{srv.name} - {srv.price}р", callback_data=f"edit_srv_{srv.id}")
    builder.button(text="➕ Добавить", callback_data="add_service")
    builder.button(text="↩️ Назад", callback_data="admin")
    return builder.adjust(1).as_markup()


def edit_service_kb(service_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить название", callback_data=f"update_srv_name_{service_id}")
    builder.button(text="💰 Изменить цену", callback_data=f"update_srv_price_{service_id}")
    builder.button(text="📂 Изменить категорию", callback_data=f"update_srv_category_{service_id}")
    builder.button(text="🗑️ Удалить услугу", callback_data=f"delete_srv_{service_id}")
    builder.button(text="↩️ Назад", callback_data="manage_services")
    return builder.adjust(1).as_markup()

def services_manage_kb(page: int = 1, per_page: int = 3) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    query = Category.select().where(Category.is_del == 0).order_by(Category.sortkey)
    total_items = query.count()
    total_pages = (total_items + per_page - 1) // per_page
    categories = query.paginate(page, per_page)

    for category in categories:
        builder.button(
            text=f"📂 {category.name}",
            callback_data=f"category_{category.id}"
        )
        
        services = Services.select().where(
            (Services.category == category) &
            (Services.is_del == 0)
        ).order_by(Services.sortkey)
        
        for service in services:
            builder.button(
                text=f"→ {service.name} ({service.price}р)", 
                callback_data=f"edit_srv_{service.id}"
            ).adjust(1)

    if total_pages > 1:
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(InlineKeyboardButton(
                text="◀️", 
                callback_data=f"serv_page_{page-1}"
            ))
        
        pagination_buttons.append(InlineKeyboardButton(
            text=f"{page}/{total_pages}", 
            callback_data="current_page"
        ))
        
        if page < total_pages:
            pagination_buttons.append(InlineKeyboardButton(
                text="▶️", 
                callback_data=f"serv_page_{page+1}"
            ))
        
        builder.row(*pagination_buttons)

    builder.row(
        InlineKeyboardButton(
            text="➕ Создать услугу",
            callback_data="add_service"
        ),
        InlineKeyboardButton(
            text="↩️ Назад",
            callback_data="admin"
        )
    )
    
    return builder.as_markup()

def back_to_admin_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура для возврата в админ-меню.
    """
    return InlineKeyboardBuilder().button(text="↩️ Назад", callback_data="admin").as_markup()

def export_data_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Пользователи (TXT)", callback_data="export_users_txt")
    builder.button(text="📝 Платежи (TXT)", callback_data="export_payments_txt")
    builder.button(text="↩️ Назад", callback_data="admin")
    return builder.adjust(1).as_markup()


def student_actions_kb(student_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить ФИО", callback_data=f"edit_student_{student_id}")
    builder.button(text="📅 Добавить занятие", callback_data=f"add_course_{student_id}")
    builder.button(text="🗑️ Удалить ученика", callback_data=f"delete_student_{student_id}")
    builder.button(text="↩️ Назад", callback_data="profile")
    return builder.adjust(1).as_markup()


def categories_manage_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=f"{cat.name} ({cat.id})", callback_data=f"edit_cat_{cat.id}")
    builder.button(text="➕ Добавить", callback_data="add_category")
    builder.button(text="↩️ Назад", callback_data="admin")
    return builder.adjust(3).as_markup()


def categories_select_kb(categories: list[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat.name, callback_data=f"select_cat_{cat.id}")
    builder.button(text="↩️ Отмена", callback_data="admin")
    builder.adjust(2)
    return builder.as_markup()