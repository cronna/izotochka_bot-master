from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    input_fullname = State()
    input_number = State()
    input_mail=State()
    input_stfullname = State()

class Buy(StatesGroup):
    payment_id = State()

class ProfileEditing(StatesGroup):
    choose_field = State()
    edit_fullname = State()
    edit_phone = State()
    edit_email = State()
    edit_student_name = State()
    add_student = State()
    add_student_f = State()
    add_course = State()

class AdminStates(StatesGroup):
    main_menu = State()
    manage_categories = State()
    edit_category = State()
    add_category_name = State()
    add_category_photo = State()
    manage_services = State()
    edit_service = State()
    add_service_name = State()  
    add_service_price = State() 
    add_service_category = State() 
    add_service_description = State() 
    add_service_photo = State() 
    manage_users = State()
    stats_period = State()
    edit_service_value = State()
    add_admin = State()
    edit_category_name = State()
    edit_category_sname = State()
    broadcast_message = State() 
    edit_category_photo = State() 