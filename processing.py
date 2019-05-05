from data_tools import *
from flask import request, session, redirect, abort
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
        user = um.get(uid)
        if user:
            return dict(user)
    return {}


def get_cuid():
    return session.get('uid', None)


def is_admin(uid):
    return um.is_admin(uid)


def login_required(api=False):
    def login_required_dec(f):
        @wraps(f)
        def login_required_wrapper(*args, **kwargs):
            if not logged_in():
                ref = request.headers.get('referer', 'index')
                if ref.endswith('login') or ref.endswith('register') or ref.endswith('logout'):
                    return redirect('index')
                else:
                    session['back'] = 'index'
                    session['next'] = request.url
                    return redirect('login')
            elif um.exists(session.get('uid', None)):
                return f(*args, **kwargs)
            else:
                if not api:
                    abort(410)
                else:
                    return {'success': False, 'error': 'Доступ ограничен'}

        return login_required_wrapper

    return login_required_dec


def sbool(v):
    return bool(v) and v != 'false'


def param_sort(posts):
    args = dict(request.args)
    key = args.pop('sort', 'time')
    reverse = sbool(args.pop('reverse', 'true'))
    consts = {k: sbool(v) for k, v in args.items()}
    rp = []
    int_k = key in ['time']
    f = int if int_k else str
    df = 0 if int_k else str
    for i in posts:
        if all(map(lambda e: bool(i.get(e[0], None)) == e[1], consts.items())):
            rp.append(i)
    rp.sort(key=lambda e: f(e.get(key, df)), reverse=reverse)
    return rp
