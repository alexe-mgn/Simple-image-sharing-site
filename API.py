from processing import *
import os

from flask import Blueprint, send_file, request, jsonify, session, current_app
from werkzeug.utils import secure_filename

from flask_restful import Api, Resource

api_app = Blueprint('API', __name__)
api = Api(api_app)


def abort_json(code, msg):
    return {'code': code, 'error': msg, 'success': False}, code


class User(Resource):

    def get(self, uid=None):
        cuid = get_cuid()
        if uid is None:
            uid = cuid
        if um.exists(uid):
            full_access = False
            if cuid:
                if cuid == uid or is_admin(cuid):
                    full_access = True
            ed = {}
            user = um.get(uid)
            for k in ['name', 'info', 'time', 'avatar_id'] + (['login', 'password'] if full_access else []):
                ed[k] = user[k]
            um.edit(uid, **ed)
            return {'success': True, 'data': ed}
        else:
            return abort_json(404, 'Пользователь не найден')

    def put(self, uid=None):
        cuid = get_cuid()
        if uid is None:
            uid = cuid
        if um.exists(uid):
            if cuid:
                if cuid == uid or is_admin(cuid):
                    data = request.json
                    inp_keys = data.keys()
                    ed = {}
                    for k in ['login', 'password', 'name', 'info', 'time', 'avatar_id']:
                        if k in inp_keys:
                            ed[k] = data[k]
                    um.edit(uid, **ed)
                    return {'success': True, 'data': ed}
                else:
                    return abort_json(403, 'Недостаточно прав')
            else:
                return abort_json(403, 'Доступ ограничен')
        else:
            return abort_json(404, 'Пользователь не найден')


class Post(Resource):

    def get(self, pid):
        if pm.exists(pid):
            post = dict(pm.get(pid))
            post['rating'] = lm.get_rating(pid)
            post['comments_number'] = len(cm.find(post_id=pid))

            cuid = get_cuid()
            data = request.json
            user_id = data.get('user_id', cuid) if data else cuid
            if user_id is not None:
                if user_id == cuid or is_admin(cuid):
                    post['user_rating'] = lm.get_user_rating(pid, user_id)
            return {'success': True, 'data': post}
        else:
            return abort_json(404, 'Публикация не найдена')

    def put(self, pid):
        if pm.exists(pid):
            cuid = get_cuid()
            if cuid is not None:
                data = request.json

                user_id = data.get('user_id', cuid)
                admin = is_admin(cuid)
                if user_id == cuid or admin:
                    if 'user_rating' in data:
                        lm.rate(pid, user_id, data['user_rating'])
                    ed = {}
                    for k in ['text'] + (['user_id', 'image_id'] if admin else []):
                        if k in data:
                            ed[k] = data[k]
                    pm.edit(pid, **ed)
                    return {'success': True, 'data': ed}
                elif 'user_rating' in data:
                    lm.rate(pid, user_id, data['user_rating'])
                    return {'success': True, 'data': {'user_rating': data['user_rating']}}
                else:
                    return abort_json(403, 'Недостаточно прав')
            else:
                return abort_json(403, 'Доступ ограничен')
        else:
            return abort_json(404, 'Публикация не найдена')

    def delete(self, pid):
        if pm.exists(pid):
            cuid = get_cuid()
            if cuid is not None:
                user_id = pm.get(pid)['user_id']
                admin = is_admin(cuid)
                if user_id == cuid or admin:
                    pm.delete(pid)
                    return {'success': True}
                else:
                    return abort_json(403, 'Недостаточно прав')
            else:
                return abort_json(403, 'Доступ ограничен')
        else:
            return abort_json(404, 'Публикация не найдена')


@api_app.route('/upload_avatar', methods=['POST'])
@login_required(api=True)
def upload_avatar():
    data = request.files.get('avatar_image', None)
    resp = {'success': False, 'id': None, 'error': ''}
    if data:
        cuid = session.get('uid', None)
        if cuid is not None:
            img_id = im.upload_secure(data.stream.read(), secure_filename(data.filename))
            if img_id is not None:
                im.delete(um[cuid]['avatar_id'])
                um.edit(cuid, avatar_id=img_id)
                resp['success'] = True
                resp['id'] = img_id
            else:
                resp['error'] = 'Невозможно сохранить файл'
        else:
            resp['error'] = 'Доступ ограничен'
    else:
        resp['error'] = 'Нет входных данных'
    return jsonify(resp)


@api_app.route('/image/<ref>')
def image(ref='0'):
    pref = 'static\\img'
    nf = 'image_not_found.png'
    if not str(ref).isdigit():
        if ref == 'not_found':
            f_name = 'not_found.jpg'
        elif ref == 'alt':
            f_name = 'image_not_found.png'
        else:
            f_name = ref
    else:
        img = im.get(int(ref))
        if img is not None:
            f_name = img['filename']
        else:
            f_name = nf
    if not os.path.isfile(os.path.join(pref, f_name)):
        f_name = nf
    fp = os.path.join(pref, f_name)
    return send_file(fp)


@api_app.route('/avatar/<int:uid>')
def avatar(uid):
    u = um[uid]
    if u:
        return image(u['avatar_id'])
    else:
        return image('alt')


api.add_resource(User, '/user/<int:uid>', '/user')
api.add_resource(Post, '/post/<int:pid>')
