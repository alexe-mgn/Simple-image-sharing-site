from processing import *

from flask import Flask, redirect, request, render_template, Markup, session, abort, jsonify

from forms import RegisterForm, LoginForm
from API import api_app

app = Flask(__name__)
app.config['SECRET_KEY'] = r'=CqWM9G&BpA&MuKTR5Qv5=8qV^2xExC9%yM7@=fA+V5nAstAf3tAR$#&+v^a2hvY'
app.register_blueprint(api_app)


@app.context_processor
def context_processor():
    return {
        'print': lambda e: Markup('<h1>{}</h1>'.format(str(e))),
        'logged_in': logged_in(),
        'user_id': session.get('uid', None),
        'user_name': session.get('name', None),
        'user_login': session.get('login', None)
    }


@app.errorhandler(404)
def error_404(*args):
    return render_template('not_found.html')


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    form = LoginForm()
    if 'uid' not in session:
        if form.validate_on_submit():
            users = um.find(login=form.login.data, password=form.password.data)
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
            if not um.login_exists(name):
                um.add(login=name, password=pas)
                new_user = um.find(login=name, password=pas)[0]
                set_session(new_user['id'])
                return render_template('login_success.html',
                                       title='Registration successful',
                                       link=get_redirect_link())
            else:
                form.login.errors.insert(0, 'Имя уже занято')
        return render_template('register.html', title='Регистрация', form=form)
    else:
        return redirect(request.headers.get('referer', 'index'))


@login_required
@app.route('/logout')
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


@login_required
@app.route('/news')
def news():
    return render_template('news.html')


@login_required
@app.route('/profile')
def own_profile():
    user = um.get(session['uid'])
    return render_template('profile.html', user=dict(user), title='Профиль')


@app.route('/profile/<int:uid>')
def profile(uid):
    user = um.get(uid)
    if user:
        return render_template('profile.html', user=dict(user), title=user['name'])
    else:
        abort(404)


if __name__ == '__main__':
    app.run(port=8080)
    database.con.commit()
