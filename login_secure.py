from flask import session


def login_user(username, access, timezone, confirmation_code):
    session['username'] = username
    session['access'] = access
    session['timezone'] = timezone
    session['confirmed'] = False if confirmation_code else True


def logout_user():
    if 'username' in session:
        session.pop('username')

    if 'access' in session:
        session.pop('access')

    if 'timezone' in session:
        session.pop('timezone')

    if 'confirmed' in session:
        session.pop('confirmed')


def get_authorization():
    current_user = {'username': '' if 'username' not in session else session['username'],
                    'access': 0 if 'access' not in session else session['access'],
                    'timezone': 0 if 'timezone' not in session else session['timezone'],
                    'confirmed': False if 'confirmed' not in session else session['confirmed']}

    return current_user
