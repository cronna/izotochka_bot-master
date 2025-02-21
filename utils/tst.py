

from models import Users, St_per, Stud, Category,Services
import os
#from keyboards import main_menu
z=6943645110
phone='79166463726'

Users.create(user_id = z,fullname='ddddd',
                 phone_number=phone,
                 username='Забел', 
                 email='mmm@gmail.com', id_crm=0)
# Services.create(id=3, category=2, name='1 занятие', price=950,id_crm=3,sortkey=1)
# Services.create(id=4, category=2, name='4 занятия', price=3200,id_crm=4,sortkey=2)
# Services.create(id=5, category=2, name='6 занятий', price=4700,id_crm=5,sortkey=3)
# Services.create(id=6, category=2, name='8 занятий', price=6200,id_crm=6,sortkey=4)

# Services.create(id=8, category=3, name='1 занятие', price=1300,id_crm=8,sortkey=5)
# Services.create(id=9, category=3, name='4 занятия', price=4400,id_crm=9,sortkey=6)
# Services.create(id=10, category=3, name='6 занятий', price=6600,id_crm=10,sortkey=7)
# Services.create(id=11, category=3, name='8 занятий', price=8800,id_crm=11,sortkey=8)
# Services.create(id=12, category=4, name='4 занятие', price=6000,id_crm=12,sortkey=9)
# Services.create(id=13, category=4, name='1 занятие', price=2000,id_crm=13,sortkey=10)
# Services.create(id=14, category=4, name='4 занятия', price=7200,id_crm=14,sortkey=11)

# Services.create(id=16, category=5, name='1 занятие', price=1800,id_crm=16,sortkey=12)
# Services.create(id=17, category=5, name='4 занятия', price=6400,id_crm=17,sortkey=13)
# Services.create(id=18, category=5, name='6 занятий', price=9400,id_crm=18,sortkey=14)

# Services.create(id=20, category=6, name='1 занятие', price=950,id_crm=20,sortkey=15)
# Services.create(id=21, category=6, name='4 занятия', price=3200,id_crm=21,sortkey=16)
# Services.create(id=22, category=6, name='6 занятий', price=4700,id_crm=22,sortkey=17)
# Services.create(id=23, category=6, name='8 занятий', price=6200,id_crm=23,sortkey=18)

# Services.create(id=25, category=7, name='1 занятие', price=1000,id_crm=25,sortkey=19)
# Services.create(id=26, category=7, name='4 занятия', price=3600,id_crm=26,sortkey=20)
# Services.create(id=27, category=7, name='6 занятий', price=5300,id_crm=27,sortkey=21)
# Services.create(id=28, category=8, name='4 занятия', price=3200,id_crm=28,sortkey=23)
# Services.create(id=29, category=8, name='6 занятий', price=4700,id_crm=29,sortkey=24)
# Services.create(id=30, category=8, name='8 занятий', price=6200,id_crm=30,sortkey=25)
# Services.create(id=31, category=9, name='1 занятие', price=950,id_crm=31,sortkey=26)
# Services.create(id=32, category=10, name='1 занятие', price=2150,id_crm=32,sortkey=30)
# Services.create(id=33, category=10, name='4 занятия', price=8000,id_crm=33,sortkey=31)
# Services.create(id=34, category=11, name='1 занятие', price=1650,id_crm=34,sortkey=32)
# Services.create(id=35, category=11, name='4 занятия', price=6000,id_crm=35,sortkey=33)
# Services.create(id=36, category=12, name='1 занятие', price=2150,id_crm=36,sortkey=34)
# Services.create(id=37, category=12, name='4 занятия', price=8000,id_crm=37,sortkey=35)
# Services.create(id=38, category=13, name='1 занятие', price=1650,id_crm=38,sortkey=36)
# Services.create(id=39, category=13, name='4 занятия', price=6000,id_crm=39,sortkey=37)
# Services.create(id=40, category=13, name='6 занятий', price=8800,id_crm=40,sortkey=38)
# Services.create(id=41, category=14, name='1 занятие', price=1800,id_crm=41,sortkey=39)
# Services.create(id=42, category=14, name='4 занятия', price=6400,id_crm=42,sortkey=40)
# Services.create(id=43, category=15, name='1 занятие', price=2800,id_crm=43,sortkey=41)
# Services.create(id=44, category=16, name='1 занятие', price=4300,id_crm=44,sortkey=42)
# Services.create(id=45, category=8, name='1 занятие', price=950,id_crm=45,sortkey=22)
# Services.create(id=46, category=9, name='4 занятия', price=3200,id_crm=46,sortkey=27)
# Services.create(id=47, category=9, name='6 занятий', price=4700,id_crm=47,sortkey=28)
# Services.create(id=48, category=9, name='8 занятий', price=6200,id_crm=48,sortkey=29)


# Services.create(id=4300, category=16, name='20.10.2024 | 15:00-17:00 | Абстрактный рисунок спирт чернилами на часах', price=1800,id_crm=15,sortkey=3)
# Services.create(id=4400, category=16, name='20.10.2024 | 12:00-14:00 | Панно на ветке из макраме', price=1600,id_crm=16,sortkey=2)
# Services.create(id=4500, category=16, name='13.10.2024 | 15:00-17:00 | Панно Море Кит эпоксидная смола', price=1500,id_crm=17,sortkey=1)

# Category.create(id=1, name = 'Катег', sname='Категор сокр', id_crm=2, sortkey=1)
# Services.create(id=1, category=1, name='Разовое', price='100',id_crm=2,sortkey=1)
   # us=385732508
# user = Users.get_or_none(Users.user_id == us)
# stud1 = St_per.get_or_none(St_per.id_per==user)


# print(user)
# if stud1 is None:
#     issud=False
#     print ('Нет учеников')
# else:
#     issud=True
#     # for stud in St_per.select().where(St_per.id_per==user.id):
#     st_per: St_per = St_per.select().where(St_per.id_per==user.id)
#     # stud: Stud =Stud.select().where(Stud.id==st_per.id_st)
    
#     for stp in st_per:
#        # stud: Stud =Stud.select().where(Stud.id==stp.id_st)
#         #stud=Stud.get(Stud==stp.id_st)
#         stud=Stud.get_by_id(stp.id_st)
#         print(stud.fullname)
#         # print(stud)
       