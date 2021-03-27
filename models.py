from app_flask import db
from datetime import datetime, timedelta
from sqlalchemy import exc, func, and_

time_str_ISO = '%Y-%m-%dT%H:%M:%SZ'  # для JS кода


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(200), unique=True)
    psw = db.Column(db.String(500), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    inn = db.Column(db.String(12), nullable=False)
    confirmation_code = db.Column(db.Integer, nullable=False, default=0)
    access = db.Column(db.Integer, nullable=False, default=0)
    reg_time = db.Column(db.DateTime, default=datetime.utcnow())
    timezone = db.Column(db.Integer, nullable=False, default=3)

    def __init__(self, username, email, psw, phone, company, inn, user_timezone, confirmation_code=None, access=0,
                 reg_time=None):
        self.username = username
        self.email = email
        self.psw = psw
        self.phone = phone
        self.company = company
        self.inn = inn
        self.timezone = user_timezone
        self.reg_time = reg_time
        self.access = access
        self.confirmation_code = confirmation_code

    def __repr__(self):
        return f'<user {self.id}:{self.username}>'


class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    post = db.Column(db.Text, nullable=False)
    time_post = db.Column(db.DateTime, default=datetime.utcnow())
    time_start = db.Column(db.DateTime, default=datetime.utcnow())
    time_close = db.Column(db.DateTime, default=datetime.utcnow())
    contract_deadline = db.Column(db.DateTime, default=datetime.utcnow())
    url_post = db.Column(db.String(150), nullable=False)
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('Users', backref=db.backref('posts', lazy='dynamic', cascade='all,delete'))

    def __init__(self, title, post, author, url_post, contract_deadline, time_start, time_close, time_post,
                 is_published):
        self.title = title
        self.post = post
        self.author = author
        self.url_post = url_post
        self.contract_deadline = contract_deadline
        self.time_start = time_start
        self.time_close = time_close
        self.time_post = time_post
        self.is_published = is_published

    def __repr__(self):
        return f'<post {self.id}:{self.title}>'


class Goods(db.Model):
    __tablename__ = 'goods'
    id = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(11), nullable=False)
    product_name = db.Column(db.String(999), nullable=False)
    unit = db.Column(db.String(9), nullable=False)

    def __init__(self, product_code, product_name, unit):
        self.product_code = product_code
        self.product_name = product_name
        self.unit = unit

    def __repr__(self):
        return f'<product {self.id}:{self.product_name}>'


# Тендер - это закупка на один товар, одна строка. Так как реальный тендер может состоять из многих товаров,
# то тендера имеют связь с Posts, post_id будет связывать все тендера-строчки в единый Тендер
# owner_price - владелец последеней(наименьшей) цены в тендере, изначально компания организатор
# для простоты сумма всегда включает НДС если он есть
class Tenders(db.Model):
    __tablename__ = 'tenders'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, default=1.00)
    step_price = db.Column(db.Integer, default=1)
    time_bet = db.Column(db.DateTime, default=datetime.utcnow())
    rate_vat = db.Column(db.Integer, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey('goods.id'))
    product = db.relationship('Goods', backref=db.backref('tenders', lazy='dynamic'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post = db.relationship('Posts', backref=db.backref('tenders', lazy='dynamic', cascade='all,delete'))
    owner_price_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner_price = db.relationship('Users', backref=db.backref('tenders', lazy='dynamic'))

    def __init__(self, quantity, price, time_bet, product, post, owner_price, step_price=1, rate_vat=0):
        self.quantity = quantity
        self.price = price
        self.time_bet = time_bet
        self.product = product
        self.post = post
        self.owner_price = owner_price
        self.step_price = step_price
        self.rate_vat = rate_vat

    def __repr__(self):
        return f'<tender summ {self.id}:{self.price * self.quantity}>'


# type_file - тип хранимого файла
# 0 - нет файла
# 1 - аватар
# 2 - скан устава
class Files(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.BLOB, nullable=True)
    name_file = db.Column(db.String(255), nullable=False)
    type_file = db.Column(db.Integer, default=0)
    owner_file_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner_file = db.relationship('Users', backref=db.backref('files', lazy='dynamic', cascade='all,delete'))

    def __init__(self, file, name_file, type_file, owner_file):
        self.file = file
        self.name_file = name_file
        self.type_file = type_file
        self.owner_file = owner_file

    def __repr__(self):
        return f'<file: {self.name_file}>'


def add_user_in_db(username, email, psw, phone, company, inn, user_timezone, confirmation_code):
    text_result = 'Новый пользователь успешно добавлен'
    addition_result = (True, text_result)
    try:
        if db.session.query(Users).filter(Users.username == username).first() is not None:
            text_result = 'Пользователь с таким логином уже существует!'
            addition_result = (False, text_result)
        elif db.session.query(Users).filter(Users.email == email).first() is not None:
            text_result = 'Пользователь с такой почтой уже существует!'
            addition_result = (False, text_result)
        elif db.session.query(Users).filter(Users.phone == phone).first() is not None:
            text_result = 'Пользователь с таким телефоном уже существует!'
            addition_result = (False, text_result)
        else:
            user = Users(username, email, psw, phone, company, inn, user_timezone, confirmation_code)
            db.session.add(user)
            db.session.commit()

    except exc.SQLAlchemyError as exp:
        db.session.rollback()
        text_result = f'Ошибка добавления пользователя в БД {str(exp)}'
        addition_result = (False, text_result)
        print(text_result)

    return addition_result


def get_info_by_username(username, get_object_model=False):
    user_info = {'id': 0, 'psw': '', 'access': 0, 'email': '', 'reg_time': 0, 'phone': '', 'company': '', 'inn': '',
                 'timezone': 0, 'confirmation_code': 1}
    try:
        query = db.session.query(Users).filter(Users.username == username)
        result = query.first()

        if result is not None:
            user_info['id'] = result.id
            user_info['email'] = result.email
            user_info['access'] = result.access
            user_info['reg_time'] = result.reg_time
            user_info['phone'] = result.phone
            user_info['company'] = result.company
            user_info['inn'] = result.inn
            user_info['timezone'] = result.timezone
            user_info['psw'] = result.psw
            user_info['confirmation_code'] = result.confirmation_code
            if get_object_model:
                user_info['object_model'] = result

    except exc.SQLAlchemyError as exp:
        print(f'Ошибка при получении данных о пользователе: {str(exp)}')

    return user_info


def get_info_by_email(email, get_object_model=False):
    user_info = {'id': 0, 'psw': '', 'access': 0, 'username': '', 'reg_time': 0, 'phone': '', 'company': '', 'inn': '',
                 'timezone': 0}
    try:
        query = db.session.query(Users).filter(Users.email == email)
        result = query.first()

        if result is not None:
            user_info['id'] = result.id
            user_info['username'] = result.username
            user_info['access'] = result.access
            user_info['reg_time'] = result.reg_time
            user_info['phone'] = result.phone
            user_info['company'] = result.company
            user_info['inn'] = result.inn
            user_info['timezone'] = result.timezone
            user_info['psw'] = result.psw
            user_info['confirmation_code'] = result.confirmation_code

            if get_object_model:
                user_info['object_model'] = result

    except exc.SQLAlchemyError as exp:
        print(f'Ошибка при получении данных о пользователе: {str(exp)}')

    return user_info


def get_list_users():
    users = []
    try:
        query = db.session.query(Users).order_by(Users.reg_time)
        result = query.first()

        if result is not None:
            users = query.all()

    except exc.SQLAlchemyError as exp:
        print(f'Ошибка при получении списка пользователей {str(exp)}')

    return users


def update_password(new_psw, email='', username=''):
    text_result = 'Новый пароль выслан на почту' if email else 'Новый пароль установлен'
    addition_result = (True, text_result)

    try:
        if email:
            user_info = get_info_by_email(email, True)
        else:
            user_info = get_info_by_username(username, True)

        if user_info.get('id') > 0:
            user = user_info.get('object_model')
            user.psw = new_psw
            db.session.commit()
        else:
            text_result = 'Пользователь с таким email не найден' if email else 'Пользователь с таким именем не найден'
            addition_result = (False, text_result)

    except exc.SQLAlchemyError as exp:
        print(f'Произошла ошибка при восстановлении/изменении пароля: {str(exp)}')
        text_result = 'Ошибка при восстановлении пароля' if email else 'Ошибка при изменении пароля'
        addition_result = (False, text_result)

    return addition_result


def update_profile(username, email, company, inn, phone, user_timezone, confirmed):
    text_result = 'Профиль обновлен'
    addition_result = (True, text_result)

    try:
        user_info = get_info_by_username(username, True)

        if user_info.get('id') > 0:
            user = user_info.get('object_model')
            user.email = email
            user.company = company
            user.inn = inn
            user.phone = phone
            user.timezone = user_timezone
            user.confirmation_code = confirmed
            db.session.commit()
        else:
            text_result = 'Пользователь с таким именем не найден'
            addition_result = (False, text_result)

    except exc.SQLAlchemyError as exp:
        print(f'Произошла ошибка при изменении профиля: {str(exp)}')
        text_result = 'Ошибка при изменении профиля'
        addition_result = (False, text_result)

    return addition_result


def get_product_by_code(product_code, get_object_model=False):
    product_info = {'id': 0, 'product_code': '', 'product_name': '', 'unit': ''}
    try:
        query = db.session.query(Goods).filter(Goods.product_code == product_code)
        result = query.first()

        if result is not None:
            product_info['id'] = result.id
            product_info['product_code'] = result.product_code
            product_info['product_name'] = result.product_name
            product_info['unit'] = result.unit

            if get_object_model:
                product_info['object_model'] = result

    except exc.SQLAlchemyError as exp:
        print(f'Ошибка при запросе к БД: {str(exp)}')

    return product_info


# ищет актуальный тендер для товара который начнется позже текущей даты
def get_actual_tender_by_product_code(product_code, get_object_model=False):
    tender_info = {'id': 0, 'quantity': 0, 'price': 0, 'step_price': 0, 'time_bet': 0, 'product': None, 'post': None}
    now = datetime.utcnow()
    try:
        query = db.session.query(Tenders).filter(and_(Tenders.post.time_start > now, Tenders.post.time_close > now,
                                                      Tenders.product.product_code == product_code))
        result = query.first()

        if result is not None:
            tender_info['id'] = result.id
            tender_info['quantity'] = result.quantity
            tender_info['price'] = result.price
            tender_info['time_bet'] = result.time_bet
            tender_info['product'] = result.product
            tender_info['post'] = result.post
            if get_object_model:
                tender_info['object_model'] = result

    except exc.SQLAlchemyError as exp:
        print(f'Ошибка при запросе к БД: {str(exp)}')

    return tender_info


# поулчает данные о посте и тендерах(товарах)
# only_last - определяет все записи получать или только последние
# username - если указан, то получаем данные о ценах участника в этом аукционе, даже если они не лучшие
def get_post_by_url(url_post, get_object_model=False, only_last=False, username=None):
    post_info = {'title': 'Статья не найдена', 'post': '---', 'author': '---', 'time_post': '---', 'time_start': '---',
                 'time_close': '---', 'contract_deadline': '---', 'is_published': False, 'tenders': [],
                 'tenders_of_user': []}
    try:
        query = db.session.query(Posts).filter(Posts.url_post == url_post)
        result = query.first()

        if result is not None:
            post_info['title'] = result.title
            post_info['post'] = result.post
            post_info['author'] = result.author.username
            post_info['time_post'] = result.time_post
            post_info['time_start'] = result.time_start
            post_info['time_close'] = result.time_close
            post_info['today'] = datetime.utcnow()
            post_info['contract_deadline'] = result.contract_deadline
            post_info['url_post'] = result.url_post
            post_info['is_published'] = result.is_published

            if username:
                post_info['tenders_of_user'] = get_last_prices_of_tender_by_user(url_post, username)

            if only_last:
                post_info['tenders'] = get_last_tenders(url_post, get_object_model)
            else:
                post_info['tenders'] = get_tenders_by_url_post(url_post, get_object_model)

            if get_object_model:
                post_info['object_model'] = result

    except exc.SQLAlchemyError as exp:
        post_info['post'] = f'Ошибка:{str(exp)}'
        print(post_info['post'])

    return post_info


# ищет тендеры для поста(с ценами всех участников), без даты так как url уникальный
# возвращает список словарей с товарами и ценами
def get_tenders_by_url_post(url_post, get_object_model=False):
    tenders_info = []
    tender_info = {'id': 0, 'quantity': 0, 'price': 0, 'step_price': 0, 'time_bet': 0, 'product_code': '',
                   'product_name': '', 'unit': '', 'owner_price_username': '', 'owner_price_inn': ''}
    try:
        query = db.session.query(Tenders).join(Posts, Posts.id == Tenders.post_id).filter(Posts.url_post == url_post)
        result = query.first()

        if result is not None:
            tenders = query.all()

            for tender in tenders:
                tender_info['id'] = tender.id
                tender_info['quantity'] = tender.quantity
                tender_info['price'] = tender.price
                tender_info['rate_vat'] = tender.rate_vat
                tender_info['step_price'] = tender.step_price
                # tender_info['time_bet'] = tender.time_bet
                # tender_info['post'] = tender.post
                tender_info['product_code'] = tender.product.product_code
                tender_info['product_name'] = tender.product.product_name
                tender_info['unit'] = tender.product.unit
                # tender_info['owner_price'] = tender.owner_price
                tender_info['owner_price_username'] = tender.owner_price.username
                tender_info['owner_price_inn'] = tender.owner_price.inn

                if get_object_model:
                    tender_info['object_model'] = tender

                tenders_info.append(tender_info.copy())
        else:
            tenders_info.append(tender_info)

    except exc.SQLAlchemyError as exp:
        tenders_info.append(tender_info)
        print(f'Ошибка при запросе к БД: {str(exp)}')

    return tenders_info


# получает только последние(актуальные) по времени тендера и с минимальной ценой
def get_last_tenders(url_post, get_object_model=False):
    tenders_info = []
    tender_info = {'id': 0, 'quantity': 0, 'price': 0, 'step_price': 0, 'time_bet': 0, 'product_code': '',
                   'product_name': '', 'unit': '', 'owner_price_username': '', 'owner_price_inn': ''}
    try:
        query = db.session.query(Tenders)
        query = query.join(Goods, Goods.id == Tenders.product_id)
        query = query.join(Posts, Posts.id == Tenders.post_id)
        query = query.filter(Posts.url_post == url_post)
        query = query.order_by(Goods.product_code, func.min(Tenders.price))
        query = query.group_by(Goods.product_code)
        result = query.first()

        if result is not None:
            tenders = query.all()

            for tender in tenders:
                tender_info['id'] = tender.id
                tender_info['quantity'] = tender.quantity
                tender_info['price'] = tender.price
                tender_info['rate_vat'] = tender.rate_vat
                tender_info['step_price'] = tender.step_price
                tender_info['product_code'] = tender.product.product_code
                tender_info['product_name'] = tender.product.product_name
                tender_info['unit'] = tender.product.unit
                tender_info['owner_price_id'] = tender.owner_price.id
                tender_info['owner_price_access'] = tender.owner_price.access
                tender_info['owner_price_username'] = tender.owner_price.username
                tender_info['owner_price_inn'] = tender.owner_price.inn

                if get_object_model:
                    tender_info['object_model'] = tender

                tenders_info.append(tender_info.copy())
        else:
            tenders_info.append(tender_info)

    except exc.SQLAlchemyError as exp:
        tenders_info.append(tender_info)
        print(f'Ошибка при запросе тендеров: {str(exp)}')

    return tenders_info


# получает последние цены участника в конкретном аукционе
# даже если участник не выиграл ни по одной цене, но сделал хоть одну прошедшую ставку, то данные об этом будут получены
def get_last_prices_of_tender_by_user(url_post, username):
    tenders_info = []
    tender_info = {'id': 0, 'quantity': 0, 'price': 0, 'step_price': 0, 'time_bet': 0, 'product_code': '',
                   'product_name': '', 'unit': '', 'owner_price_username': '', 'owner_price_inn': ''}

    try:
        query = db.session.query(Tenders)
        query = query.join(Goods, Goods.id == Tenders.product_id)
        query = query.join(Posts, Posts.id == Tenders.post_id)
        query = query.join(Users, Users.id == Tenders.owner_price_id)
        query = query.filter(and_(Posts.url_post == url_post, Users.username == username))
        query = query.order_by(Goods.product_code, func.min(Tenders.price))
        query = query.group_by(Goods.product_code)
        result = query.first()

        if result is not None:
            tenders = query.all()

            for tender in tenders:
                tender_info['id'] = tender.id
                tender_info['quantity'] = tender.quantity
                tender_info['price'] = tender.price
                tender_info['rate_vat'] = tender.rate_vat
                tender_info['step_price'] = tender.step_price
                tender_info['product_code'] = tender.product.product_code
                tender_info['product_name'] = tender.product.product_name
                tender_info['unit'] = tender.product.unit
                tender_info['owner_price_id'] = tender.owner_price.id
                tender_info['owner_price_access'] = tender.owner_price.access
                tender_info['owner_price_username'] = tender.owner_price.username
                tender_info['owner_price_inn'] = tender.owner_price.inn
                tenders_info.append(tender_info.copy())

    except exc.SQLAlchemyError as exp:
        tenders_info.append(tender_info)
        print(f'Ошибка при запросе тендеров: {str(exp)}')

    return tenders_info


# получает всех участников тендера в порядке времени начала участия
# для восстановления порядковых номеров как во время торгов
def get_all_users_in_tender(url_post):
    users_tender = {}

    try:
        query = db.session.query(Tenders)
        query = query.join(Posts, Tenders.post_id == Posts.id)
        query = query.filter(Posts.url_post == url_post)
        query = query.order_by(Tenders.time_bet)
        query = query.group_by(Tenders.owner_price_id)
        result = query.first()

        if result is not None:
            tenders = query.all()
            serial_number = 0

            for tender in tenders:
                serial_number += 1
                users_tender[tender.owner_price_id] = serial_number

    except exc.SQLAlchemyError as exp:
        print(f'Ошибка при запросе участников торгов: {str(exp)}')

    return users_tender


# получает данные о владельцах цен для формирования колонок и сами цены в том виде в котором они нужны для html формы
# игнорируя администратра ресурса(Users.access == 0) это нужно для динамического формирования таблицы при торгах
# функцией JS ajax_get_current_tenders
def get_tenders_with_owners_price(url_post, current_username, current_access, get_object_model=False):
    tenders_users = []  # здесь строки всех участников кроме текущего
    tenders_info = []  # здесь строки всех участников, но впереди идут строки текущего участника, если они есть
    tender_info = {'id': 0, 'quantity': 0, 'price': 0, 'step_price': 0, 'time_bet': 0, 'product_code': '',
                   'product_name': '', 'unit': '', 'owner_price_id': 0, 'owner_price_username': '',
                   'owner_price_access': 0, 'owner_price_inn': '', 'time_close': 0,
                   'current_username': current_username, 'current_access': current_access}

    try:
        query = db.session.query(Tenders)
        query = query.join(Posts, Posts.id == Tenders.post_id)
        query = query.join(Users, Users.id == Tenders.owner_price_id)
        query = query.filter(Posts.url_post == url_post)
        result = query.first()

        if result is not None:
            # server_timezone = datetime.now(timezone.utc).astimezone().utcoffset().seconds / 60 / 60
            tenders = query.all()

            for tender in tenders:
                tender_info['id'] = tender.id
                tender_info['quantity'] = tender.quantity
                tender_info['step_price'] = tender.step_price
                tender_info['product_code'] = tender.product.product_code
                tender_info['product_name'] = tender.product.product_name
                tender_info['unit'] = tender.product.unit
                # остальное нужно превратить в столбцы во фронтэнде
                tender_info['price'] = tender.price
                tender_info['owner_price_id'] = tender.owner_price.id
                tender_info['owner_price_username'] = tender.owner_price.username
                tender_info['owner_price_access'] = tender.owner_price.access
                tender_info['time_close'] = tender.post.time_close.strftime(time_str_ISO)
                tender_info['current_username'] = current_username
                tender_info['current_access'] = current_access

                if get_object_model:
                    tender_info['object_model'] = tender

                if tender_info['owner_price_username'] == current_username:
                    tenders_info.append(tender_info.copy())
                else:
                    tenders_users.append(tender_info.copy())

            tenders_info.extend(tenders_users)  # присоединю к текщему пользователю всех остальных
        else:
            tenders_info.append(tender_info)

    except exc.SQLAlchemyError as exp:
        tenders_info.append(tender_info)
        print(f'Ошибка при запросе к БД: {str(exp)}')

    return tenders_info


def add_post_in_db(title, text_post, username, contract_deadline, time_start, time_close, is_published,
                   list_of_products):
    text_result = 'Объявление о тендере успешно добавлено.'
    addition_result = (True, text_result)
    now = datetime.utcnow()
    user_info = get_info_by_username(username, True)
    author = user_info.get('object_model')
    # начало и закрытие торгов указываем в местном времени значит нужно его привести к UTC +0 в БД
    time_start = from_localtime_to_utc0(time_start, user_info.get('timezone'))
    time_close = from_localtime_to_utc0(time_close, user_info.get('timezone'))
    url_post = ''.join(x for x in title if x.isalpha() or x.isdigit())
    url_post = transliterate(url_post)

    if author is not None:
        try:
            post_info = get_post_by_url(url_post, True)
            post = post_info.get('object_model')

            if post is not None:
                text_result = 'Статья с таким url уже существует!'
                addition_result = (False, text_result)
            else:
                post = Posts(title, text_post, author, url_post, contract_deadline, time_start, time_close, now,
                             is_published)
                db.session.add(post)
                db.session.flush()

                # нужно добавить товары из списка
                for row_product in list_of_products:
                    product_info = get_product_by_code(row_product.get('product_code'), True)
                    product = product_info.get('object_model')

                    if product is None:
                        product = Goods(row_product.get('product_code'), row_product.get('product_name'),
                                        row_product.get('unit'))

                    db.session.add(product)
                    db.session.flush()
                    tender = Tenders(row_product.get('quantity'), row_product.get('start_price'), now, product, post,
                                     author, row_product.get('step_price'), row_product.get('rate_vat'))
                    db.session.add(tender)
                    db.session.flush()

                db.session.commit()

        except exc.SQLAlchemyError as exp:
            db.session.rollback()
            text_result = f'Ошибка добавления статьи в БД: {str(exp)}'
            addition_result = (False, text_result)
    else:
        text_result = 'Ошибка добавления объявления: не удалось определить автора!'
        addition_result = (False, text_result)

    return addition_result


def update_post_and_tender(title, text_post, username, contract_deadline, time_start, time_close, is_published,
                           list_of_products_new, url_post):
    text_result = 'Изменения записаны.'
    addition_result = (True, text_result)
    user_info = get_info_by_username(username, True)
    author = user_info.get('object_model')
    # начало и закрытие торгов указываем в местном времени значит нужно его привести к UTC +0 в БД
    time_start = from_localtime_to_utc0(time_start, user_info.get('timezone'))
    time_close = from_localtime_to_utc0(time_close, user_info.get('timezone'))
    now = datetime.utcnow()
    # если title не изменился, то следующие 2 строки создададут такой же url как и передан в url_post
    url_post_new = ''.join(x for x in title if x.isalpha() or x.isdigit())
    url_post_new = transliterate(url_post_new)

    try:
        post_info = get_post_by_url(url_post, True)
        post = post_info.get('object_model')

        if post is not None:
            post.title = title
            post.time_post = now
            post.time_start = time_start
            post.time_close = time_close
            post.contract_deadline = contract_deadline
            post.post = text_post
            post.url_post = url_post_new
            post.author = author
            post.is_published = is_published

            # удалю все тендеры
            for row_product in post_info.get('tenders'):
                db.session.delete(row_product.get('object_model'))

            # и тупо запишу новые
            for row_product in list_of_products_new:
                product_info = get_product_by_code(row_product.get('product_code'), True)
                product = product_info.get('object_model')

                if product is None:
                    product = Goods(row_product.get('product_code'), row_product.get('product_name'),
                                    row_product.get('unit'))
                    db.session.add(product)
                    db.session.flush()

                tender = Tenders(row_product.get('quantity'), row_product.get('start_price'), now, product, post,
                                 author, row_product.get('step_price'), row_product.get('rate_vat'))
                db.session.add(tender)

            db.session.commit()

    except exc.SQLAlchemyError as exp:
        db.session.rollback()
        text_result = f'Ошибка изменения статьи и тендеров в БД: {str(exp)}'
        addition_result = (False, text_result)

    return addition_result


def delete_post(url_post):
    text_result = 'Изменения записаны.'
    addition_result = (True, text_result)
    post_info = get_post_by_url(url_post, True)
    post = post_info.get('object_model')

    if post is not None:
        try:
            db.session.delete(post)
            db.session.commit()
        except exc.SQLAlchemyError as exp:
            print(f'Ошибка при удалении поста {str(exp)}')
            text_result = 'Не удалось удалить пост'
            addition_result = (False, text_result)

    return addition_result


# обновляет данные тендера новыми ценами клиента
# сейчас не использую, так как надо запоминать цену каждого участника на конкретный товар, это делает следующая функция
def update_tender(product_code, client_price, url_post, username):
    updated = True
    now = datetime.utcnow()
    try:
        query = db.session.query(Tenders)
        query = query.join(Posts, Posts.id == Tenders.post_id)
        query = query.join(Goods, Goods.id == Tenders.product_id)
        query = query.filter(and_(Posts.url_post == url_post, now > Posts.time_start, now < Posts.time_close,
                                  Goods.product_code == product_code))
        result = query.first()

        if result is not None:
            user_info = get_info_by_username(username, True)
            user = user_info.get('object_model')
            result.price = client_price
            result.time_bet = now
            result.owner_price = user
            db.session.commit()
        else:
            updated = False

    except exc.SQLAlchemyError as exp:
        db.session.rollback()
        print(f'Ошибка при установке новой цены от клиента {str(exp)}')
        updated = False

    return updated


# вместо перезаписи строки товара в таблице новой ценой, добавляет новую строку в таблице перезаписывая только свои цены
# не трогая цены других учатников, формируя историю торгов в разрезе участников,запоминая только последнюю цену на товар
# каждого из участников
def add_or_update_tender(product_code, client_price, url_post, username):
    updated = True
    user_info = get_info_by_username(username, True)
    user_id = user_info.get('id')
    now = datetime.utcnow()
    try:
        query = db.session.query(Tenders)
        query = query.join(Posts, Posts.id == Tenders.post_id)
        query = query.join(Goods, Goods.id == Tenders.product_id)
        query = query.filter(and_(Posts.url_post == url_post, now > Posts.time_start, now < Posts.time_close,
                                  Goods.product_code == product_code, Tenders.owner_price_id == user_id))
        result = query.first()

        if result is not None:
            # print(f'Участник {username} ОБНОВИЛ свою старую цену для {product_code}')
            result.price = client_price
            result.time_bet = now
            db.session.commit()
        else:
            # если не нашли цену принадлежащую этому участнику, то создадим новую строку с ценой
            query = db.session.query(Tenders)
            query = query.join(Posts, Posts.id == Tenders.post_id)
            query = query.join(Goods, Goods.id == Tenders.product_id)
            query = query.filter(and_(Posts.url_post == url_post, now > Posts.time_start, now < Posts.time_close,
                                      Goods.product_code == product_code))
            result = query.first()

            if result is not None:
                # print(f'Участник {username} ДОБАВИЛ свою цену для {product_code}')
                post_info = get_post_by_url(url_post, True)
                post = post_info.get('object_model')
                product_info = get_product_by_code(product_code, True)
                product = product_info.get('object_model')
                user = user_info.get('object_model')
                tender = Tenders(result.quantity, client_price, now, product, post, user, result.step_price,
                                 result.rate_vat)
                db.session.add(tender)
                db.session.commit()
            else:
                updated = False

    except exc.SQLAlchemyError as exp:
        db.session.rollback()
        print(f'Ошибка при добавлении новой цены от клиента {str(exp)}')
        updated = False

    return updated


# здесь только проверяем цены и решаем стоит ли обновлять их в тендере
# list_of_new_prices - список с новыми ценами из формы тендера на сайте
# tenders_info - список словарей с данными о текущем тендере из БД
def check_new_price(url_post, tenders_info, list_of_new_prices, username, time_close):
    text_result = 'Ваши новые цены приняты сервером!'
    result = True
    errors_code_product = []  # тут сохраним все коды товаров которые не прошли по цене

    if not list_of_new_prices:
        text_result = 'Не обнаружены изменения в ценах!'
        result = False
        addition_result = (result, text_result)
        return addition_result

    for new_data in list_of_new_prices:
        number_row = new_data.get('number_row')
        product_code = new_data.get('product_code')
        client_price = new_data.get('client_price')

        for server_data in tenders_info:
            server_product_code = server_data.get('product_code')
            server_price = server_data.get('price')

            if server_product_code == product_code and server_price > client_price > 0:
                updated = add_or_update_tender(product_code, client_price, url_post, username)

                if not updated:  # из-за ошибки при записи в БД тоже добавлю код товара в список непринятых сервером
                    errors_code_product.append(number_row)
                else:
                    # найдем оставшееся время до закрытия торгов и если последняя ставка сделана в последние 10 минут
                    # то добавим к времени закрытия торгов еще 10 минут
                    time_until_closing = (time_close - datetime.utcnow()).total_seconds()

                    if 0 < time_until_closing < 600:
                        post_info = get_post_by_url(url_post, True)
                        post = post_info.get('object_model')
                        post.time_close = post_info['time_close'] + timedelta(seconds=600)
                        db.session.commit()
                break

            elif server_product_code == product_code and server_price <= client_price and server_data.get(
                    'owner_price_username') != username:
                errors_code_product.append(number_row)
                text_result = 'Номера строк товаров цены на которые не прошли:'

    if len(errors_code_product) == len(list_of_new_prices):
        result = False
        text_result = 'Все ваши цены не прошли, так как есть уже цены равные вашим или ниже!'
    elif errors_code_product:
        text_result = f"{text_result} {', '.join(errors_code_product)}"

    addition_result = (result, text_result)
    return addition_result


# type_file: 1 - аватар, 2 - документ (pdf, jpg)
def add_file_user(file, name_file, username, type_file, max_count_files):
    text_result = 'Файл загружен'
    uploaded = True

    files_info = get_files_user(username)

    if len(files_info) >= max_count_files:
        text_result = f'Запрещено загружать более {max_count_files} файлов'
        uploaded = False
    else:
        user_info = get_info_by_username(username, True)
        user_id = user_info.get('id')
        user = user_info.get('object_model')
        try:
            query = db.session.query(Files).filter(and_(Files.owner_file_id == user_id, Files.name_file == name_file))
            result = query.first()

            if result is not None:
                result.file = file
                db.session.commit()
            else:
                file_db = Files(file, name_file, type_file, user)
                db.session.add(file_db)
                db.session.commit()

        except exc.SQLAlchemyError as exp:
            text_result = 'Не удалось загрузить файл'
            uploaded = False

    return uploaded, text_result


def delete_file_user(username, file_id):
    text_result = 'Файл удален'
    deleted = True
    try:
        query = db.session.query(Files)
        query = query.join(Users, Users.id == Files.owner_file_id)
        query = query.filter(and_(Users.username == username, Files.id == file_id))
        result = query.first()

        if result is not None:
            db.session.delete(result)
            db.session.commit()
        else:
            text_result = 'Не удалось удалить файл'
            deleted = False

    except exc.SQLAlchemyError as exp:
        text_result = 'Не удалось удалить файл'
        deleted = False

    return deleted, text_result


# получаем все файлы пользователя в словаре - id файла:имя файла
def get_files_user(username):
    files_info = {}
    try:
        query = db.session.query(Files)
        query = query.join(Users, Users.id == Files.owner_file_id)
        query = query.filter(Users.username == username)
        result = query.first()

        if result is not None:
            files = query.all()

            for file in files:
                files_info[file.id] = file.name_file

    except exc.SQLAlchemyError as exp:
        print('Не удалось получить файлы пользователя')

    return files_info


def get_file_user_by_file_id(file_id):
    file_data = {'file': None, 'name_file': ''}
    try:
        query = db.session.query(Files).filter(Files.id == file_id)
        result = query.first()

        if result is not None:
            file_data['file'] = result.file
            file_data['name_file'] = result.name_file

    except exc.SQLAlchemyError as exp:
        print(f'Ошибка: {str(exp)}')

    return file_data


# Для 1С что бы получить список всех существующих тендеров
def get_all_url_posts(limit_number_posts):
    urls = {}
    try:
        query = db.session.query(Posts).order_by(Posts.time_post.desc()).limit(limit_number_posts)

        if query.first() is not None:
            posts = query.all()
            for post in posts:
                urls[post.url_post] = post.title

    except exc.SQLAlchemyError:
        print('Нет ни одного поста')

    return urls


# only_active - только активные тендера
def get_list_posts(page, posts_per_page, only_active=False, not_published=False):
    page_of_posts = {}
    try:
        if only_active:
            now = datetime.utcnow()
            page_of_posts = db.session.query(Posts).filter(
                and_(Posts.time_start < now, Posts.time_close > now, Posts.is_published != not_published)).order_by(
                Posts.time_post.desc()).paginate(page, posts_per_page, False)
        else:
            page_of_posts = db.session.query(Posts).filter(Posts.is_published != not_published).order_by(
                Posts.time_post.desc()).paginate(page, posts_per_page, False)
    except exc.SQLAlchemyError:
        print('Нет ни одного поста')

    return page_of_posts


def create_site_db():
    db.create_all()


def transliterate(str_to_translate):
    slovar = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
              'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
              'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
              'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
              'ю': 'u', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
              'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
              'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
              'Ц': 'C', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
              'Ю': 'U', 'Я': 'YA', ',': '', '?': '', ' ': '_', '~': '', '!': '', '@': '', '#': '',
              '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '-': '', '=': '', '+': '',
              ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
              '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i',
              'Є': 'e', '—': ''}

    for key in slovar:
        str_to_translate = str_to_translate.replace(key, slovar[key])
    return str_to_translate


def get_timezones():
    timezones = [(0, 'UTC+0 Лондон, Дублин, Лиссабон'), (1, 'UTC+1 Брюссель, Париж, Мадрид'),
                 (2, 'UTC+2 Калининград, Афины, Киев'), (3, 'UTC+3 Москва, Санкт-Петербург, Минск'),
                 (4, 'UTC+4 Самара, Баку, Тбилиси'), (5, 'UTC+5 Екатеринбург, Исламабад, Ташкент'),
                 (6, 'UTC+6 Омск, Новосибирск, Бишкек'), (7, 'UTC+7 Красноярск, Абакан, Бангкок'),
                 (8, 'UTC+8 Иркутск, Улан-Удэ, Пекин'), (9, 'UTC+9 Якутск, Благовещенск, Токио'),
                 (10, 'UTC+10 Владивосток, Магадан, Сахалин'), (11, 'UTC+11 Соломомновы острова'),
                 (12, 'UTC+12 Камчатка, Веллингтон, Фиджи'), (-1, 'UTC-1 Азорские острова'),
                 (-2, 'UTC-2 Среднеатлантическое время'), (-3, 'UTC-3 Бразилиа, Буэнос-Айрес'),
                 (-4, 'UTC-4 Атлантическое время(Канада)'),
                 (-5, 'UTC-5 Восточное время (США и Канада)'),
                 (-6, 'UTC-6 Центральное время(США и Канада'),
                 (-7, 'UTC-7 Горное время(США и Канада)'),
                 (-8, 'UTC-8 Тихоокеанское время (США и Канада)'),
                 (-9, 'UTC-9 Аляска'), (-10, 'UTC-10 Гавайи'),
                 (-11, 'UTC-11 Остров Мидуэй, Самоа'), (-12, 'UTC-12 Эневеток, Кваджалейн')]

    return timezones


def from_utc0_to_localtime(utc_time, user_timezone):
    return utc_time + timedelta(hours=user_timezone)


def from_localtime_to_utc0(utc_time, user_timezone):
    return utc_time - timedelta(hours=user_timezone)


def check_latin(str_for_checked):
    result = True
    latin_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_'

    for letter in str_for_checked:
        if letter not in latin_string:
            result = False
            break

    return result
