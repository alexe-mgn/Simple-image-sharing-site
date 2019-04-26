from functools import wraps

from flask import Flask, url_for, redirect, request, render_template, session, abort

from data_tools import *
from forms import RegisterForm, LoginForm

database = Database('data.db')
um = UsersModel(database)
app = Flask(__name__)
app.config['SECRET_KEY'] = r'=CqWM9G&BpA&MuKTR5Qv5=8qV^2xExC9%yM7@=fA+V5nAstAf3tAR$#&+v^a2hvY'


def set_session(uid):
    session['uid'] = uid
    u = um[uid]
    session['name'] = u['name']


def del_session():
    session.pop('uid')
    session.pop('name')


def logged_in():
    return 'uid' in session


def login_required(f):
    @wraps(f)
    def login_required_wrapper(*args, **kwargs):
        if not logged_in():
            if request.headers.get('referer', 'index').endswith('login'):
                return redirect('index')
            else:
                return redirect('login')
        else:
            return f(*args, **kwargs)

    return login_required_wrapper


def get_redirect_link():
    if request.headers.get('referer', 'index') == request.url:
        return 'index'
    else:
        return request.headers.get('referer', 'index')


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    form = LoginForm()
    if 'uid' not in session:
        if form.validate_on_submit():
            users = um.find_user(name=form.login.data, password=form.password.data)
            if users:
                user = users[0]
                set_session(user['id'])
            else:
                form.errors['account'] = ['Неверные данные для входа']
    if 'uid' not in session:
        return render_template('login.html', title='Вход', form=form)
    else:
        return render_template('login_success.html',
                               title='Login success',
                               link=get_redirect_link())


@app.route('/register', methods=['GET', 'POST'])
def register_form():
    form = RegisterForm()
    if not logged_in():
        if form.validate_on_submit():
            name, pas = form.login.data, form.password.data
            if not um.user_exists(name):
                um.add_user(name, pas)
                new_user = um.find_user(name=name, password=pas)[0]
                set_session(new_user['id'])
                return render_template('login_success.html',
                                       title='Registration successful',
                                       link=get_redirect_link())
            else:
                form.login.errors.insert(0, 'Имя уже занято')
        return render_template('register.html', title='Регистрация', form=form)
    else:
        return redirect(request.headers.get('referer', 'index'))


@app.route('/logout')
@login_required
def logout_page():
    del_session()
    return render_template('logout.html', link=get_redirect_link(), title='Выход')


@app.route('/')
@app.route('/index')
def index():
    if logged_in():
        return redirect('news')
    else:
        return render_template('index.html')


@app.route('/news')
def news():
    if not logged_in():
        return redirect('index')
    else:
        return render_template('news.html')


@app.route('/profile')
def profile():
    if not logged_in():
        return redirect('/login')
    else:
        user = um.get_user(session['uid'])
        return render_template('profile.html', profile=dict(user), title='Домашняя страница')


if __name__ == '__main__':
    app.run(port=8080)
    database.con.commit()
