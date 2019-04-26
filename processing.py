from data_tools import *
from flask import request, session, redirect
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
    session.pop('uid')
    session.pop('login')
    session.pop('name')


def logged_in():
    return 'uid' in session


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
