from data_tools import *
from flask import request, session, redirect
from flask import current_app as app
from functools import wraps

DATABASE = 'data.db'
SECRET_KEY = r'=CqWM9G&BpA&MuKTR5Qv5=8qV^2xExC9%yM7@=fA+V5nAstAf3tAR$#&+v^a2hvY'

database = Database('data.db')
um = UsersModel(database)
im = ImagesModel(database)
pm = PublicationsModel(database)
cm = CommentsModel(database)
lm = LikesModel(database)


def set_session(uid):
    session['uid'] = uid
    u = um[uid]
    session['login'] = u['login']
    session['name'] = u['name']


def del_session():
    session.pop('uid', None)
    session.pop('login', None)
    session.pop('name', None)


def logged_in():
    return 'uid' in session


def get_session_user():
    uid = session.get('uid', None)
    if uid is not None:
        user = dict(um.get(uid))
    else:
        user = {}
    print(user)
    return user


def get_redirect_link():
    if request.headers.get('referer', 'index') == request.url:
        return 'index'
    else:
        return request.headers.get('referer', 'index')


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
