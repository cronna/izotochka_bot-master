import requests
import json
from types import SimpleNamespace
import uuid
from datetime import datetime, timedelta

phone_number="9165877672"
fullname="Забелич Денис Григорьевич"
useremail="zabelichdg@mail.ru"
tovar="Изо"
price='100'
total_price='100'
desc1="Тестовый счет"
desc2="Тестовый счет"
par_id='1'





exp_d=datetime.utcnow()+timedelta(days=3) + timedelta(hours=3)
exp_d=str(exp_d.isoformat("T", "milliseconds")+"Z")
print (exp_d)

data={
          "payment_data": {
       "amount": {
              "value": total_price,
              "currency": "RUB"
            },
     "payment_method_data":{"type":"sbp"},
            "receipt": {
              "customer": {
                "email": useremail
              },
              "items": [
                {
                  "description": tovar,
                  "quantity": 1.000,
                  "amount": {
                    "value": price,
                    "currency": "RUB"
                  },
                  "vat_code": 1,
                  "payment_mode": "full_payment",
                  "payment_subject": "service",
                  "tax_system_code": 6,
                  
                }
              ]
            },
            "capture": True,
            "description": desc1,
            "metadata": {
              "order_id": "1"
            }
          },
          "merchant_customer_id": useremail,
          "cart": [
            {
              "description": tovar,
              "price": {
                "value": price,
                "currency": "RUB"
              },
              "quantity": 1.000
            }
          ],
          "delivery_method_data": {
            "type": "self"
          },
          "locale": "ru_RU",
          "expires_at": exp_d,
          "description": desc2,
          "metadata": {
            "par_id": par_id
          }
}


print(data)
dataj=json.dumps(data)
# print(dataj)
#headers = {'Idempotence-Key':'9e9w0b5f-897f-5227-9701-516f49e1a987', 'Content-Type':'application/json'}
#print(headers)

headers = {'Idempotence-Key':str(uuid.uuid4()), 'Content-Type':'application/json'}
#print(headers)
#
#Auth={'466776':'live_n21gP-I4_MOrhU_qJXuvksTierpplPt_WwyylJJTLsg'}
#Auth={'454437':'test_Yx2aiW5Tnezx5fXlf8n8nn2JTxQV-8YpQoRsMtkFu54'}
Auth={'452550':'live_6L_H3cZBgnOYZPeFWKbowkk1WtqVi9u0TXQ0G8Vq8wY'}

r = requests.post('https://api.yookassa.ru/v3/invoices',data=dataj, headers=headers,auth=('452550', 'live_6L_H3cZBgnOYZPeFWKbowkk1WtqVi9u0TXQ0G8Vq8wY'))
res=r.json()
#print(res)
print(res['id'])
#print(res['status'])
print(res['delivery_method']['url'])

