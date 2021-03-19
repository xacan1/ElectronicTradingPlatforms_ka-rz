import json
import random
import string
from datetime import datetime
from io import BytesIO

from flask import render_template, url_for, g, flash, redirect, session, abort, request, send_file
from werkzeug.security import generate_password_hash, check_password_hash

import models
from adminka import admin_initialization
from app_flask import admin_panel, app
from forms import LoginForm, RegistrationForm, AddEditPostForm, TenderForm, PasswordChangeForm, PasswordRecoveryForm, \
    EditProfileForm, UploadFilesForm
from login_secure import login_user, logout_user, get_authorization
from send_email import EmailSender

title = 'АО «КАРЗ»'
admin_initialization(admin_panel)


@app.before_request
def before():
    if not hasattr(g, 'site_db_exist'):
        g.site_db_exist = True
        models.create_site_db()


@app.route('/')
@app.route('/index')
def index():
    current_user = get_authorization()
    current_year = datetime.now().year

    return render_template('index.html', title=title, title_page='', current_user=current_user,
                           current_year=current_year)


@app.route('/about')
def about():
    current_user = get_authorization()
    current_year = datetime.now().year

    return render_template('about.html', title='О компании', title_page='О компании', current_user=current_user,
                           current_year=current_year)


@app.route('/catalog/<url_cat>')
@app.route('/catalog')
def catalog(url_cat=None):
    current_user = get_authorization()
    current_year = datetime.now().year
    title_cat = 'Продукция и услуги'
    page = 'catalog.html'

    if not url_cat:
        url_cat = 'repair'

    if url_cat:
        page = f'{url_cat}.html'

        if url_cat == 'repair':
            title_cat = 'Ремонт и обслуживание авиационных двигателей'
        elif url_cat == 'lycoming':
            title_cat = 'Двигатель Lycoming IO-540'
        elif url_cat == 'arriel':
            title_cat = 'Двигатель Arriel 2B1'
        elif url_cat == 'fire':
            title_cat = 'Факельные установки'
        elif url_cat == 'reducers':
            title_cat = 'Редукторы'
        elif url_cat == 'centralizers':
            title_cat = 'Центраторы звеньев'
        elif url_cat == 'wrenches':
            title_cat = 'Ключи ударные накидные'
        else:
            page = 'catalog.html'

    return render_template(page, title=title_cat, title_page=title_cat, current_user=current_user, url_cat=url_cat,
                           current_year=current_year)


@app.route('/contacts')
def contacts():
    current_user = get_authorization()
    current_year = datetime.now().year

    return render_template('contacts.html', title='Контакты', title_page='Контакты', current_user=current_user,
                           current_year=current_year)


@app.route('/list_tenders')
def list_tenders():
    current_user = get_authorization()
    current_year = datetime.now().year
    page = request.args.get('page', 1, type=int)
    posts = models.get_list_posts(page, app.config.get('POSTS_PER_PAGE'))
    announcements = posts.items if posts else []
    next_url = url_for('list_tenders', page=posts.next_num) if posts and posts.has_next else None
    prev_url = url_for('list_tenders', page=posts.prev_num) if posts and posts.has_prev else None

    return render_template('list_tenders.html', title='Анонсы тендеров', title_page='Анонсы тендеров',
                           current_user=current_user, announcements=announcements, next_url=next_url, prev_url=prev_url,
                           current_year=current_year)


@app.route('/list_tenders/<url_post>')
def show_post(url_post=None):
    page = None
    current_user = get_authorization()
    current_year = datetime.now().year
    post_info = models.get_post_by_url(url_post, False, True, current_user.get('username'))

    if not post_info['tenders']:
        page = redirect(url_for('list_tenders'))

    if not page:
        page = render_template('post.html', post_info=post_info, title='Информация об аукционе',
                               title_page='Информация об аукционе', current_user=current_user,
                               current_year=current_year)

    return page


@app.route('/results_tenders/<url_post>')
def show_result_tender(url_post=None):
    page = None
    current_user = get_authorization()
    current_year = datetime.now().year

    if not current_user.get('username'):
        page = redirect(url_for('login'))

    users_tender = models.get_all_users_in_tender(url_post)
    post_info = models.get_post_by_url(url_post, False, True, current_user.get('username'))
    post_info['today'] = models.from_utc0_to_localtime(post_info['today'], current_user.get('timezone'))
    post_info['time_start_local'] = models.from_utc0_to_localtime(post_info['time_start'], current_user.get('timezone'))
    post_info['time_close_local'] = models.from_utc0_to_localtime(post_info['time_close'], current_user.get('timezone'))

    if users_tender:
        for tender in post_info['tenders']:
            tender['serial_number_user'] = users_tender[tender['owner_price_id']]
    else:
        for tender in post_info['tenders']:
            tender['serial_number_user'] = tender['owner_price_id']

    if not page:
        page = render_template('result_tender.html', post_info=post_info, title='Результаты торгов',
                               title_page='Результаты торгов', current_user=current_user, current_year=current_year)

    return page


@app.route('/login', methods=['POST', 'GET'])
def login():
    page = None
    current_user = get_authorization()
    current_year = datetime.now().year
    form_login = LoginForm()

    if current_user['username']:
        page = redirect(url_for('profile', username=current_user['username']))
    elif form_login.validate_on_submit():
        user_info = models.get_info_by_username(form_login.username.data)
        pass_ok = check_password_hash(user_info['psw'], form_login.psw.data)

        if user_info['id'] > 0 and pass_ok:
            login_user(form_login.username.data, user_info['access'], user_info['timezone'],
                       user_info['confirmation_code'])
            page = redirect(url_for('profile', username=form_login.username.data))
        else:
            flash('Пользователя с таким логином или паролем не существует!', category='error')

    if not page:
        page = render_template('login.html', title='Авторизация', current_user=current_user, form=form_login,
                               current_year=current_year)

    return page


@app.route('/logout')
def logout():
    logout_user()
    current_year = datetime.now().year

    return render_template('index.html', title=title, title_page='', current_year=current_year)


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    page = None
    current_year = datetime.now().year
    form_registration = RegistrationForm()

    if form_registration.validate_on_submit():
        if not models.check_latin(form_registration.username.data):
            flash('Логин должен быть на латинице! Допускаются цифры и нижнее подчеркивание', category='error')
        elif form_registration.psw.data.isalpha() or form_registration.psw.data.isdigit():
            flash('Пароль должен содержать буквы и цифры!', category='error')
        else:
            hash_psw = generate_password_hash(form_registration.psw.data)
            confirmation_code = random.randint(100000, 999999)
            result, msg = models.add_user_in_db(form_registration.username.data, form_registration.email.data, hash_psw,
                                                form_registration.phone.data, form_registration.company.data,
                                                form_registration.inn.data, form_registration.user_timezone.data,
                                                confirmation_code)

            if result:
                flash(msg, category='success')
                page = redirect(url_for('login'))
            else:
                flash(msg, category='error')

    if not page:
        page = render_template('registration.html', title='Регистрация', title_page='Заполните форму регистрации',
                               form=form_registration, current_year=current_year)

    return page


@app.route('/user_agreement')
def user_agreement():
    current_year = datetime.now().year
    current_user = get_authorization()

    return render_template('user_agreement.html', title='Пользовательское соглашение',
                           title_page='Пользовательское соглашение', current_year=current_year)


@app.route('/password_change', methods=['POST', 'GET'])
def password_change():
    page = None
    current_year = datetime.now().year
    current_user = get_authorization()
    form_password_change = PasswordChangeForm()

    if form_password_change.validate_on_submit():
        old_psw = form_password_change.old_psw.data
        new_psw = form_password_change.new_psw.data
        user_info = models.get_info_by_username(current_user.get('username'))
        pass_ok = check_password_hash(user_info['psw'], old_psw)
        if not pass_ok:
            flash('Текущий пароль введен не верно!', category='error')
        elif new_psw.isalpha() or new_psw.isdigit():
            flash('Пароль должен содержать буквы и цифры!', category='error')
        else:
            hash_psw = generate_password_hash(new_psw)
            result, msg = models.update_password(new_psw=hash_psw, username=current_user.get('username'))
            if result:
                flash(msg, category='success')
            else:
                flash(msg, category='error')

    if not page:
        page = render_template('password_change.html', title='Изменение пароля', current_user=current_user,
                               title_page='Изменение пароля', form=form_password_change, current_year=current_year)

    return page


@app.route('/password_recovery', methods=['POST', 'GET'])
def password_recovery():
    page = None
    current_year = datetime.now().year
    form_password_recovery = PasswordRecoveryForm()

    if form_password_recovery.validate_on_submit():
        email = form_password_recovery.email.data
        new_password = str(random.randint(1, 9)).join(random.choices(string.ascii_lowercase + string.digits, k=3))
        hash_psw = generate_password_hash(new_password)
        result, msg = models.update_password(new_psw=hash_psw, email=email)

        if result:
            flash(msg, category='success')
            message = f'Ваш новый пароль: {new_password}'
            email_sender = EmailSender(app.config.get('MAIL_USERNAME'), app.config.get('MAIL_PASSWORD'), email,
                                       'Восстановление пароля ka-rz.ru',
                                       'team.ka-rz.ru')
            email_sender.send_message(message)
        else:
            flash(msg, category='error')

    if not page:
        page = render_template('password_recovery.html', title='Восстановление пароля',
                               title_page='Восстановление пароля', form=form_password_recovery,
                               current_year=current_year)

    return page


@app.route('/edit_profile/<username>', methods=['POST', 'GET'])
@app.route('/edit_profile', methods=['POST', 'GET'])
def edit_profile(username=None):
    page = None
    current_year = datetime.now().year
    current_user = get_authorization()
    my_account = not username  # если мы зашли в свой аккаунт, то оставим подтверждение аккаунта без изменений

    if not username:
        username = current_user.get('username')

    form_edit_profile = EditProfileForm()

    if form_edit_profile.validate_on_submit():
        email = form_edit_profile.email.data
        company = form_edit_profile.company.data
        inn = form_edit_profile.inn.data
        phone = form_edit_profile.phone.data
        user_timezone = form_edit_profile.user_timezone.data

        if my_account:
            confirmed = current_user.get('confirmed')
        else:
            confirmed = 0 if form_edit_profile.confirmed.data else 1

        result, msg = models.update_profile(username, email, company, inn, phone, user_timezone, confirmed)

        if result:
            if my_account:
                user_info = models.get_info_by_username(username)
                login_user(username, user_info.get('access'), user_info.get('timezone'),
                           user_info.get('confirmation_code'))

            flash(msg, category='success')
        else:
            flash(msg, category='error')
    else:
        user_info = models.get_info_by_username(username)
        form_edit_profile.email.data = user_info.get('email')
        form_edit_profile.company.data = user_info.get('company')
        form_edit_profile.inn.data = user_info.get('inn')
        form_edit_profile.phone.data = user_info.get('phone')
        form_edit_profile.user_timezone.data = user_info.get('timezone')
        form_edit_profile.confirmed.data = not user_info.get('confirmation_code')

    if not page:
        page = render_template('edit_profile.html', title='Редактирование профиля', title_page='Редактирование профиля',
                               current_user=current_user, form=form_edit_profile, current_year=current_year,
                               username_profile=username)

    return page


@app.route('/upload_files', methods=['POST', 'GET'])
def upload_files():
    current_year = datetime.now().year
    current_user = get_authorization()
    form_upload_files = UploadFilesForm()

    if form_upload_files.validate_on_submit():
        data_upload = form_upload_files.file.data
        file = data_upload.read()
        filename = models.transliterate(data_upload.filename)  # проблемы с кириллицей так что преобразуем имя файла
        uploaded, msg = models.add_file_user(file, filename, current_user.get('username'), 2)

        if uploaded:
            flash(msg, category='success')
        else:
            flash(msg, category='error')

    return render_template('upload_files.html', title='Загрузка файла', title_page='Загрузка файла',
                           current_user=current_user, form=form_upload_files, current_year=current_year)


@app.route('/download_files/<username>/<filename>')
def download_files(username, filename):
    current_user = get_authorization()

    if not current_user.get('access') and username != current_user.get('username'):
        abort(401)

    file_data = models.get_file_user(username, filename)

    return send_file(BytesIO(file_data), attachment_filename=filename, as_attachment=True)


@app.route('/profile/<username>')
@app.route('/profile')
def profile(username=None):
    current_user = get_authorization()
    current_year = datetime.now().year

    if not username:
        username = current_user.get('username')

    if not current_user.get('access') and username != current_user.get('username'):
        abort(401)

    user_info = models.get_info_by_username(username)
    #  если такого пользователя нет, то вернемся на нашу страницу профиля
    if user_info.get('id') == 0:
        return redirect(url_for('profile', username=current_user.get('username')))

    info_for_profile = {'Имя пользователя': username}
    files_info = models.get_files_user(username)

    for key in user_info:
        if key == 'psw':
            continue
        elif key == 'reg_time':
            reg_time = models.from_utc0_to_localtime(user_info[key], current_user['timezone'])
            info_for_profile['Время регистрации'] = reg_time.strftime("%d-%m-%Y %H:%M")
        elif key == 'access':
            info_for_profile['Права'] = 'Пользователь' if user_info[key] == 0 else 'Администратор'
        elif key == 'email':
            info_for_profile['Email'] = user_info[key]
        elif key == 'phone':
            info_for_profile['Телефон'] = user_info[key]
        elif key == 'company':
            info_for_profile['Компания'] = user_info[key]
        elif key == 'inn':
            info_for_profile['ИНН'] = user_info[key]
        elif key == 'timezone':
            timezones = models.get_timezones()
            info_for_profile['Часовой пояс'] = [t[1] for t in timezones if t[0] == user_info[key]][0]
        elif key == 'confirmation_code':
            info_for_profile['Учетная запись подтверждена'] = 'Ожидает подтверждения администратора' if user_info[
                key] else 'Да'

    return render_template('profile.html', title='Личный кабинет', title_page='Профиль пользователя',
                           info_for_profile=info_for_profile, current_user=current_user, username_profile=username,
                           current_year=current_year, files=files_info)


@app.route('/list_users')
def list_users():
    current_user = get_authorization()
    current_year = datetime.now().year

    if not current_user.get('access'):
        abort(401)

    users = models.get_list_users()

    return render_template('list_users.html', title='Список пользователей', title_page='Список пользователей',
                           current_user=current_user, current_year=current_year, users=users)


@app.route('/add_tender', methods=['GET', 'POST'])
def add_tender():
    current_user = get_authorization()
    current_year = datetime.now().year

    if not current_user.get('access'):
        abort(401)

    form_add_edit_tender = AddEditPostForm()

    if form_add_edit_tender.validate_on_submit():
        list_of_products = json.loads(form_add_edit_tender.list_products_JSON.data)

        if not list_of_products:
            flash('Не добавлено ни одного товара в тендер!', category='error')
        else:
            result, msg = models.add_post_in_db(form_add_edit_tender.title_tender.data, form_add_edit_tender.post.data,
                                                current_user.get('username'),
                                                form_add_edit_tender.contract_deadline.data,
                                                form_add_edit_tender.time_start.data,
                                                form_add_edit_tender.time_close.data, list_of_products)

            if result:
                flash(msg, category='success')
            else:
                flash(msg, category='error')

    return render_template('add_edit_tender.html', title='Добавление тендера', title_page='Добавление нового тендера',
                           current_user=current_user, form=form_add_edit_tender, current_year=current_year)


@app.route('/edit_tender/<url_post>', methods=['GET', 'POST'])
def edit_tender(url_post):
    current_user = get_authorization()
    current_year = datetime.now().year

    if not current_user['access']:
        abort(401)

    post_info = None
    form_add_edit_tender = AddEditPostForm()

    if form_add_edit_tender.validate_on_submit():
        list_of_products = json.loads(form_add_edit_tender.list_products_JSON.data)

        if not list_of_products:
            flash('Не добавлено ни одного товара в тендер!', category='error')
        else:
            result, msg = models.update_post_and_tender(form_add_edit_tender.title_tender.data,
                                                        form_add_edit_tender.post.data,
                                                        current_user['username'],
                                                        form_add_edit_tender.contract_deadline.data,
                                                        form_add_edit_tender.time_start.data,
                                                        form_add_edit_tender.time_close.data, list_of_products,
                                                        url_post)

            if result:
                flash(msg, category='success')
            else:
                flash(msg, category='error')

    else:
        # если страница просто обновлена, то перезаполним данные формы
        post_info = models.get_post_by_url(url_post, False, True)
        form_add_edit_tender.title_tender.data = post_info['title']
        form_add_edit_tender.time_start.data = models.from_utc0_to_localtime(post_info['time_start'],
                                                                             current_user['timezone'])
        form_add_edit_tender.time_close.data = models.from_utc0_to_localtime(post_info['time_close'],
                                                                             current_user['timezone'])
        form_add_edit_tender.contract_deadline.data = post_info['contract_deadline']
        form_add_edit_tender.post.data = post_info['post']
        form_add_edit_tender.list_products_JSON.data = json.dumps(post_info['tenders'])

    return render_template('add_edit_tender.html', title='Изменение тендера', title_page='Изменение тендера',
                           current_user=current_user, post_info=post_info, form=form_add_edit_tender,
                           current_year=current_year)


@app.route('/delete_tender/<url_post>')
def delete_tender(url_post):
    page = None
    current_user = get_authorization()
    current_year = datetime.now().year

    if not current_user['access'] or not url_post:
        abort(401)

    result, msg = models.delete_post(url_post)

    if result:
        page = redirect(url_for('list_tenders'))
    else:
        flash(msg, category='error')

    if not page:
        page = redirect(url_for('edit_tender', url_post=url_post))

    return page


@app.route('/tender/<url_post>', methods=['GET', 'POST'])
def show_tender(url_post):
    current_user = get_authorization()
    current_year = datetime.now().year

    if not current_user.get('username'):
        page = redirect(url_for('login'))
    else:
        post_info = models.get_post_by_url(url_post, False, True)

        if not post_info['tenders']:
            page = redirect(url_for('list_tenders'))
        else:
            form_tender = TenderForm()

            if not form_tender.tender_info_JSON.data:
                form_tender.tender_info_JSON.data = '[]'

            if form_tender.validate_on_submit():
                list_of_new_prices = json.loads(form_tender.tender_info_JSON.data)

                if current_user.get('access') == 0:
                    result, msg = models.check_new_price(url_post, post_info.get('tenders'), list_of_new_prices,
                                                         current_user.get('username'), post_info.get('time_close'))
                elif not current_user.get('confirmed'):
                    result = False
                    msg = 'Для участия в торгах требуется подтверждение учетной записи администратором!'
                else:
                    result = False
                    msg = 'Администратор сайта не может участвовать в торгах!'

                if result:
                    flash(msg, category='success')
                else:
                    flash(msg, category='error')

                return redirect(url_for('show_tender', url_post=url_post))

            page = render_template('tender.html', title=f"Закупки по тендеру {post_info.get('title')}",
                                   title_page=f"Закупки по тендеру {post_info.get('title')}", post_info=post_info,
                                   current_user=current_user, form=form_tender, current_year=current_year)

    return page


# защита сервиса от атак https://habr.com/ru/post/246699/
@app.route('/api/<api_method>', methods=['POST'])
def api_post(api_method):
    current_user = get_authorization()
    response_JSON = '[]'
    token = request.headers.get('x-client-key')

    if api_method == 'get_table_tender' and current_user.get('username') and 'url_post' in request.values:
        # получение текущих цен из фронтэнда сюда идет запрос функции ajax_get_current_tenders
        tenders_info = models.get_tenders_with_owners_price(request.values['url_post'], current_user.get('username'),
                                                            current_user.get('access'))
        response_JSON = json.dumps(tenders_info)

    elif api_method == 'upload_tender_from_1c' and token == app.config.get('TOKEN_API') and request.data:
        tender_data = request.get_json()  # json.loads(request.data)  # распарсим тело запроса в словарь
        post_info = models.get_post_by_url(tender_data.get('url_post'), False, True)
        contract_deadline = datetime.strptime(tender_data.get('contract_deadline'), '%d%m%Y%H%M%S')
        time_start = datetime.strptime(tender_data.get('time_start'), '%d%m%Y%H%M%S')
        time_close = datetime.strptime(tender_data.get('time_close'), '%d%m%Y%H%M%S')

        if post_info['tenders']:
            result, msg = models.update_post_and_tender(tender_data.get('title'), tender_data.get('post'),
                                                        tender_data.get('username'),
                                                        contract_deadline, time_start, time_close,
                                                        tender_data.get('list_of_products'),
                                                        tender_data.get('url_post'))
        else:
            result, msg = models.add_post_in_db(tender_data.get('title'), tender_data.get('post'),
                                                tender_data.get('username'),
                                                contract_deadline, time_start, time_close,
                                                tender_data.get('list_of_products'))

        response_JSON = json.dumps(msg, ensure_ascii=False)

    return response_JSON


@app.route('/api/<api_method>', methods=['GET'])
@app.route('/api/<api_method>/<url_post>', methods=['GET'])
def api_get(api_method, url_post=None):
    current_user = get_authorization()
    response_JSON = '[]'
    token = request.headers.get('x-client-key')

    if token != app.config.get('TOKEN_API'):
        response_api = {'error': 'Ошибка загрузки с сайта: Ошибка авторизации в API'}
        response_JSON = json.dumps(response_api, ensure_ascii=False)
        return response_JSON

    if api_method == 'download_tender_to_1c':

        if not url_post:
            response_api = {'error': 'Ошибка загрузки с сайта: Не передан url_post'}
            response_JSON = json.dumps(response_api, ensure_ascii=False)
            return response_JSON

        username = 'ADMINISTRATOR'
        user_info = models.get_info_by_username(username, False)
        post_info = models.get_post_by_url(url_post, False, True)

        if post_info['tenders']:
            post_info['time_post'] = models.from_utc0_to_localtime(post_info['time_post'],
                                                                   user_info.get('timezone')).strftime('%Y%m%d%H%M%S')
            post_info['time_start'] = models.from_utc0_to_localtime(post_info['time_start'],
                                                                    user_info.get('timezone')).strftime('%Y%m%d%H%M%S')
            post_info['time_close'] = models.from_utc0_to_localtime(post_info['time_close'],
                                                                    user_info.get('timezone')).strftime('%Y%m%d%H%M%S')
            post_info['contract_deadline'] = models.from_utc0_to_localtime(post_info['contract_deadline'],
                                                                           user_info.get('timezone')).strftime(
                '%Y%m%d%H%M%S')
            post_info['today'] = post_info['today'].strftime('%Y%m%d%H%M%S')
            response_JSON = json.dumps(post_info, ensure_ascii=False)

    elif api_method == 'get_all_url_posts':
        limit_number_posts = request.headers.get('number_posts')
        limit_number_posts = int(limit_number_posts) if limit_number_posts and limit_number_posts.isdigit() else 30
        posts = models.get_all_url_posts(limit_number_posts)
        response_JSON = json.dumps(posts, ensure_ascii=False)

    return response_JSON


@app.errorhandler(404)
def page_not_found(error):
    current_user = get_authorization()
    current_year = datetime.now().year

    return render_template('page404.html', title='Страница не найдена', title_page='Упс! Нет такой страницы.',
                           current_user=current_user, current_year=current_year), 404


@app.errorhandler(413)
def file_size_exceeded(error):
    current_user = get_authorization()
    current_year = datetime.now().year
    max_file_size = (app.config.get('MAX_CONTENT_LENGTH') - 1) / 1024 / 1024
    flash(f"Файл превышает допустимый размер для загрузки в {max_file_size} Мб", category='error')

    return render_template('upload_files.html', title='Файлы пользователя', title_page='Файлы пользователя',
                           current_user=current_user, form=None, current_year=current_year), 200


# Сохранение данных страницы и корзины в сессии
def send_data_in_session(list_dict):
    pass


def get_data_from_session():
    pass


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


if __name__ == '__main__':
    app.run()
