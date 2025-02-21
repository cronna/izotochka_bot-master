from peewee import *

# db = SqliteDatabase('database.db')

# SQLite database using WAL journal mode and 64MB cache.
db = SqliteDatabase('/path/to/app.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64})

# Connect to a MySQL database on network.
db = MySQLDatabase('IZO', user='root', password='',
                         host='127.0.0.1', port=3306)

class Users(Model):
    id = AutoField()
    # id = IntegerField(primary_key=True)
    user_id = CharField(null=True)
    username = TextField()
    fullname = TextField()
    phone_number = TextField()
    email = TextField()
    id_crm =IntegerField()
    is_admin = BooleanField(default=False)

    class Meta:
        database = db

class AdminUsers(Model):
    user_id = IntegerField(unique=True)
    
    class Meta:
        database = db


class Stud(Model):
    id = AutoField()
    fullname = TextField()
    id_crm =IntegerField()
    is_del = BooleanField(default=False)

    class Meta:
        database = db

class St_per(Model):
    id = AutoField()
    id_st = ForeignKeyField(model=Stud, backref='st_per', column_name='id_st')
    id_per = ForeignKeyField(model=Users, backref='st_per', column_name='id_per')

    class Meta:
        database = db


class Category(Model):
    id = AutoField()
    name = TextField() #Полное имя для чеков и уведомлений
    sname=TextField() #Сокращенное имя для кнопок
    is_del=IntegerField(default=0)
    id_crm=IntegerField(default=0)
    sortkey=IntegerField(default=0) #Для сортировки
    image = TextField(null=True)

    class Meta:
        database = db


class Services(Model):
    id = AutoField()
    category = ForeignKeyField(model=Category, backref='services')
    name = TextField()
    price = IntegerField()
    is_del=IntegerField(default=0)
    id_crm=IntegerField(default=0)
    sortkey=IntegerField(default=0) 
    description = TextField(null=True)  
    image = TextField(null=True)  

    class Meta:
        database = db


class PaymentsT(Model):
    id = AutoField()
    id_st = ForeignKeyField(model=Stud, backref='paymentsT', column_name='id_st')
    user = ForeignKeyField(model=Users, backref='paymentsT', null=True)
    service = ForeignKeyField(model=Services, backref='paymentsT')
    price = IntegerField()
    payment_date = DateTimeField()
    id_uch = TextField()
    p_status = TextField()
    ch_status = TextField()
    id_crm =IntegerField()
    finished = BooleanField(default=False)
   

    class Meta:
        database = db

class inv(Model):
    id = IntegerField(primary_key=True)
    user_id = IntegerField()
    fullname = TextField()
    email = TextField()
    summ=IntegerField()
    id_inv =TextField(null=True)
    id_pay =TextField(null=True)
    status=TextField(null=True)
    finished = BooleanField(null=True)
    

    class Meta:
        database = db


class invd(Model):
    id = IntegerField(primary_key=True)
    inv=ForeignKeyField(model=inv, backref='invd')
    stud_id = IntegerField(null=True)
    fullname =TextField()
    price = IntegerField()
    tovar=TextField()
    service = IntegerField()
    

    class Meta:
        database = db


class StudentCourses(Model):
    student = ForeignKeyField(Stud, backref='courses')
    service = ForeignKeyField(Services)
    start_date = DateField()
    end_date = DateField(null=True)
    is_active = BooleanField(default=True)

    class Meta:
        database = db
