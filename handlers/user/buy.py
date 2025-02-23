import datetime
import os
import json

from aiogram import F, Router
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from utils.models import Users, Services, PaymentsT, Category
import uuid
from yookassa import Configuration, Payment
from os import getenv
import asyncio
from aiogram.fsm.context import FSMContext
from utils.states import Buy
from utils.keyboards import user_show_pay_kb


buy_router = Router()


Configuration.account_id = '466776'
Configuration.secret_key = 'live_n21gP-I4_MOrhU_qJXuvksTierpplPt_WwyylJJTLsg'

# Configuration.account_id ='454437'
# Configuration.secret_key ='test_Yx2aiW5Tnezx5fXlf8n8nn2JTxQV-8YpQoRsMtkFu54'
# print(Configuration.account_id)
# print(Configuration.secret_key)


@buy_router.callback_query(F.data.split()[0] == 'buy')
async def buy_handler(callback: CallbackQuery, state: FSMContext):
    # db.connection()
    user: Users = Users.get_or_none(Users.user_id == callback.from_user.id)
    service: Services = Services.get_by_id(int(callback.data.split()[1]))
    id_stud=int(callback.data.split()[2])
    category: Category = Category.get_by_id(service.category_id)
    tovar=category.name+" "+ service.name
    labels = [LabeledPrice(label=service.name,
                           amount=service.price * 100)]
    
    print(user.phone_number, tovar,service.price)    
   
    #await callback.message.delete()
   
   
    payment1 = Payment.create({
	                            "amount": {
                                "value": service.price,
                                 "currency": "RUB"
	    },
 	                             "confirmation": {
                                   "type": "redirect",
                                 "return_url": "https://t.me/izotochka_bot"
  		  },
   		                         "capture": True,
  	                             "description": tovar,
                                 "payment_method_data":{"type":"sbp"},
                            
  	                             "metadata":{"id_tel":user.phone_number,
  	                             "id_st":user.fullname},
  	                             "merchant_customer_id":user.email,
  	
                                 "receipt": {
                               "customer": {
        #    "full_name": "Иванов Иван Иванович",
                               "email": user.email
                                     },
                             "items": [
            {
                             "description": tovar,
                              "quantity": 1.000,
                              "amount": {
                              "value": service.price,
                              "currency": "RUB"
                },
                             "vat_code": 1,
                           "payment_mode": "full_payment",
                           "payment_subject": "service",
                           "tax_system_code":6
            },
           
  		      ]
		    }
		
  	  
  	  
  	  
  	  
		}, 								
  	  uuid.uuid4())
    
    paymentt: PaymentsT = PaymentsT.create(user=user,
                                        service=service,
                                        price=service.price,
                                        payment_date=datetime.datetime.now(),
                                        id_uch=payment1.id,
                                        p_status=payment1.status,
                                        ch_status="",
                                        id_crm=0,
                                        id_st_id=id_stud
                                        )
      


    
    print(payment1.confirmation.confirmation_url)
    await state.update_data(payment_id=payment1.id)
    await state.set_state(Buy.payment_id)
    await callback.message.edit_text(f'Для оплаты перейдите по ссылке {payment1.confirmation.confirmation_url}')
    # db.close
    #await callback.message.edit_text('Для оплаты перейдите по ссылке', reply_markup=user_show_pay_kb(payment1))

# @buy_router.callback_query(F.data == 'conf')
# async def check_payment(state: FSMContext):
# 	print(payment_id)
# 	data = await state.get_data()
# 	payment_id=data['payment_id']
# 	print(payment_id)
# 	payment1 = json.loads((Payment.find_one(payment_id)).json())
# 	while payment1['status'] == 'pending':
# 		payment1 = json.loads((Payment.find_one(payment_id)).json())
# 		await asyncio.sleep(3)
# 		print("ddd12")

	# if payment1['status']=='succeeded':
	# 	print("SUCCSESS RETURN")
	# 	print(payment1)
	# 	#return True
	# else:
	# 	print("BAD RETURN")
	# 	print(payment1)
	# 	#return False

@buy_router.pre_checkout_query(F.func(lambda query: True))
async def pre_checkout_query_handle(event: PreCheckoutQuery):
    await event.bot.edit_text_pre_checkout_query(event.id, ok=True)


@buy_router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    paymentt: PaymentsT = PaymentsT.get_by_id(int(message.successful_payment.invoice_payload))
    await message.edit_text('''✅ Спасибо!
Ваш платеж принят, информация направлена администратору''')
    text = f'''🆕 Платёж #{paymentt.id}
<b>Данные о клиенте</b>
👤 ФИО: <i>{paymentt.user.fullname}</i>
📱 Номер телефона: <i>{paymentt.user.phone_number}</i>
🆔 Username: <i>{paymentt.user.username if paymentt.user.username != "None" else "отсутствует"}</i>

<b>Данные о покупке</b>
🗂️ Категория: <i>{paymentt.service.category.name}</i>
🤝 Услуга: <i>{paymentt.service.name}</i>
💵 Стоимость: <i>{paymentt.price}₽</i>
🗓️ Дата: <i>{paymentt.payment_date}</i>'''
    paymentt.finished = True
    paymentt.save()
    await message.bot.send_message(os.getenv('CHANNEL_ID'), text, parse_mode="HTML")
