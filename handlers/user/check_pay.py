import asyncio
from utils.models import PaymentsT,Users, Stud
from yookassa import Configuration, Payment
import os
#from main import bot

async def check_payment(bot):
    while True:
        await asyncio.sleep(5)
     #    print ("Проверяю статус")
        for p in PaymentsT.select().where(PaymentsT.finished==0):
                pmnt=Payment.find_one(p.id_uch)
                print ("Есть неоплаченный")
                #print (pmnt.status)
                #print(Users.get_by_id(p.user_id).user_id)
                if pmnt.status!='pending':
                     
                     p.finished = 1
                     #p.save()
                     p.p_status= pmnt.status
                     p.save()
                if pmnt.status=='succeeded':
                     print ('Успех')
                     id_bot_usr=Users.get_by_id(p.user_id).user_id
                     st_name=Stud.get_by_id(p.id_st).fullname
                     await bot.send_message(id_bot_usr, f'''✅ Спасибо!🎨👨‍🎨
Ваш платеж 💰принят, информация направлена 💸 администратору👩‍🏫
Чек отправлен на {p.user.email}
                                                                                  
<b>Данные о покупке</b>
👤 Ученик: <i>{st_name}</i>
🗂️ Категория: <i>{p.service.category.name}</i>
🤝 Услуга: <i>{p.service.name}</i>
💵 Стоимость: <i>{p.price}₽</i>
🗓️ Дата: <i>{p.payment_date}</i>
🗓️ Транзакция: <i>{p.id_uch}</i>''', parse_mode="HTML")
                     text = f'''🆕 Платёж #{p.id}
<b>Данные о клиенте</b>
👤 ФИО: <i>{p.user.fullname}</i>
📱 Ученик: <i>{st_name}</i>
📱 Номер телефона: <i>{p.user.phone_number}</i>
📱 Почта: <i>{p.user.email}</i>
🆔 Username: <i>{p.user.username if p.user.username != "None" else "отсутствует"}</i>

<b>Данные о покупке</b>
🗂️ Категория: <i>{p.service.category.name}</i>
🤝 Услуга: <i>{p.service.name}</i>
💵 Стоимость: <i>{p.price}₽</i>
🗓️ Дата: <i>{p.payment_date}</i>
🗓️ Транзакция: <i>{p.id_uch}</i>'''
                     await bot.send_message(os.getenv('CHANNEL_ID'), text, parse_mode="HTML")
                     

            
