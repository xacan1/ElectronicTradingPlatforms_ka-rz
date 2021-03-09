from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FieldList, FormField, \
    SelectField, IntegerField, FileField
from wtforms.fields.html5 import DateField, DateTimeLocalField, TelField
from wtforms.validators import InputRequired, Length, EqualTo, Email
from datetime import datetime
from models import get_timezones
import config

flask_config = config.ProductionConfig()


class LoginForm(FlaskForm):
    username = StringField('Логин или email', validators=[InputRequired('Введите логин')])
    psw = PasswordField('Пароль', validators=[InputRequired('Введите пароль'),
                                              Length(min=flask_config.MIN_PASSWORD_LENGTH,
                                                     max=flask_config.MAX_PASSWORD_LENGTH,
                                                     message=f'Пароль должен быть от {flask_config.MIN_PASSWORD_LENGTH} до {flask_config.MAX_PASSWORD_LENGTH} символов')])
    # remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[InputRequired('Заполните поле логин'),
                                                Length(min=flask_config.MIN_LOGIN_LENGTH,
                                                       max=flask_config.MAX_LOGIN_LENGTH,
                                                       message=f'Логин должен быть от {flask_config.MIN_LOGIN_LENGTH} до {flask_config.MAX_LOGIN_LENGTH} символов')])
    email = StringField('Email', validators=[InputRequired('Заполните email'), Email('Введен не корректный email')])
    phone = TelField('Телефон', validators=[InputRequired('Заполните телефон'),
                                            Length(min=11, message='Номер телефона слишком короткий')])
    company = StringField('Название компании или ФИО ИП',
                          validators=[InputRequired('Заполните наименование компании'),
                                      Length(min=3, message='Наименование компании должно быть не менее 3-х символов')])
    inn = StringField('ИНН компании или ИП', validators=[InputRequired('Заполните ИНН')])
    user_timezone = SelectField('Ваша временная зона UTC', coerce=int, choices=get_timezones(), default=3,
                                validators=[InputRequired('Повторите пароль')])
    psw = PasswordField('Пароль', validators=[InputRequired('Введите пароль'),
                                              Length(min=flask_config.MIN_PASSWORD_LENGTH,
                                                     max=flask_config.MAX_PASSWORD_LENGTH,
                                                     message=f'Пароль должен быть от {flask_config.MIN_PASSWORD_LENGTH} до {flask_config.MAX_PASSWORD_LENGTH} символов')])
    repeat_psw = PasswordField('Повторите пароль', validators=[InputRequired('Повторите пароль'),
                                                               EqualTo('psw', message='Пароли не совпадают')])
    accept_user_agreement = BooleanField(validators=[InputRequired('Для регистрации нужно принять условия соглашения')])
    submit = SubmitField('Зарегистрироваться')


# это вложенная форма, так что валидации тут не нужны, их трудно отслеживать
class FieldsProduct(FlaskForm):
    product_code = StringField('Код номенклатуры', default='0', id='product_code')
    product_name = StringField('Наименование', default='', id='product_name')
    unit = StringField('Единица измерения', default='шт.', id='unit')
    step_price = IntegerField('Шаг цены', default=0, id='step_price')
    quantity = IntegerField('Количество', default=0, id='quantity')
    start_price = IntegerField('Начальная цена', default=0, id='start_price')
    rate_vat = IntegerField('Ставка НДС', default=0, id='rate_vat')

    class Meta:
        csrf = False


class AddEditPostForm(FlaskForm):
    title_tender = StringField(
        'Заголовок',
        validators=[InputRequired('Заполните заголовок тендера'),
                    Length(min=5, max=120,
                           message='Заголовок тендера должен быть не короче 5 символов и не длинее 120')])
    time_start = DateTimeLocalField('Открытие торгов', validators=[InputRequired('Заполните дату')],
                                    default=datetime.utcnow(), format='%Y-%m-%dT%H:%M')
    time_close = DateTimeLocalField('Закрытие торгов', validators=[InputRequired('Заполните дату')],
                                    default=datetime.utcnow(), format='%Y-%m-%dT%H:%M')
    contract_deadline = DateField('Срок исполнения контракта', default=datetime.utcnow())
    post = TextAreaField('Текст объявления о тендере', validators=[InputRequired('Заполните текст объявления')])
    list_products_JSON = StringField('Скрытое поле для отправки JSON на сервер из формы',
                                     validators=[InputRequired('Не добавлены товары!')])
    product_fields = FieldList(FormField(FieldsProduct), min_entries=1, label='Product')
    submit = SubmitField('Добавить / изменить тендер')


class TenderForm(FlaskForm):
    tender_info_JSON = StringField('Скрытое поле для сохранения введенных цен пользователя',
                                   validators=[InputRequired('Нет данных для сохранения')])
    submit = SubmitField('Утвердить изменения')


class PasswordChangeForm(FlaskForm):
    old_psw = PasswordField('Нынешний пароль', validators=[InputRequired('Введите ваш текущий пароль')])
    new_psw = PasswordField('Новый пароль', validators=[InputRequired('Введите новый пароль'),
                                                        Length(min=flask_config.MIN_PASSWORD_LENGTH,
                                                               max=flask_config.MAX_PASSWORD_LENGTH,
                                                               message=f'Пароль должен быть от {flask_config.MIN_PASSWORD_LENGTH} до {flask_config.MAX_PASSWORD_LENGTH} символов')])
    repeat_new_psw = PasswordField('Повторите новый пароль', validators=[InputRequired('Повторите новый пароль'),
                                                                         EqualTo('new_psw',
                                                                                 message='Пароли не совпадают')])
    submit = SubmitField('Изменить пароль')


class PasswordRecoveryForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired('Заполните email'), Email('Введен не корректный email')])
    submit = SubmitField('Восстановить пароль')


class EditProfileForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired('Заполните email'), Email('Введен не корректный email')])
    phone = TelField('Телефон', validators=[InputRequired('Заполните телефон'),
                                            Length(min=11, message='Номер телефона слишком короткий')])
    company = StringField('Название компании или ФИО ИП',
                          validators=[InputRequired('Заполните наименование компании'),
                                      Length(min=3, message='Наименование компании должно быть не менее 3-х символов')])
    inn = StringField('ИНН компании или ИП', validators=[InputRequired('Заполните ИНН')])
    user_timezone = SelectField('Ваша временная зона UTC', coerce=int, choices=get_timezones(), default=3,
                           validators=[InputRequired('Повторите пароль')])
    confirmed = BooleanField('Учетная запись подтверждена')
    submit = SubmitField('Применить')


class UploadFilesForm(FlaskForm):
    file = FileField('Выберите файл для загрузки', validators=[InputRequired('Выберите файл')])
    submit = SubmitField('Загрузить')
