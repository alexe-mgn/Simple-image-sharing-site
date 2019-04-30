from processing import *
import os
from flask import Blueprint, send_file, request, jsonify, session, current_app
from werkzeug.utils import secure_filename

api_app = Blueprint('API', __name__)


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


@api_app.route('/update_name', methods=['POST'])
@login_required(api=True)
def update_name():
    data = request.get_data(as_text=True)
    resp = {'success': False, 'error': '', 'text': ''}
    if data:
        cuid = session.get('uid', None)
        if cuid is not None:
            um.edit(cuid, name=data)
            resp['success'] = True
            resp['text'] = data
        else:
            resp['error'] = 'Доступ ограничен'
    return jsonify(resp)


@api_app.route('/update_info', methods=['POST'])
@login_required(api=True)
def update_info():
    data = request.get_data(as_text=True)
    resp = {'success': False, 'error': '', 'text': ''}
    if data:
        cuid = session.get('uid', None)
        if cuid is not None:
            um.edit(cuid, info=data)
            resp['success'] = True
            resp['text'] = data
        else:
            resp['error'] = 'Доступ ограничен'
    else:
        resp['error'] = 'Нет входных данных'
    return jsonify(resp)


@api_app.route('/update_post_text/<int:pid>', methods=['GET'])
@login_required(api=True)
def get_post_rating(pid):
    data = request.get_data(as_text=True)
    resp = {'success': False, 'error': '', 'text': ''}
    cuid = session.get('uid', None)
    if data:
        if cuid is not None:
            res = lm.get_rating(pid, cuid)
            resp['success'] = True
            resp['value'] = res
        else:
            resp['error'] = 'Доступ ограничен'
    else:
        resp['error'] = 'Нет входных данных'
    return jsonify(resp)


@api_app.route('/post_rating/<int:pid>', methods=['GET'])
@login_required(api=True)
def get_post_rating(pid):
    resp = {'success': False, 'error': '', 'value': None}
    cuid = session.get('uid', None)
    if cuid is not None:
        res = lm.get_rating(pid, cuid)
        resp['success'] = True
        resp['value'] = res
    else:
        resp['error'] = 'Доступ ограничен'
    return jsonify(resp)


# Хорошее место для накрутки оценок
@api_app.route('/post_rating/<int:pid>/<int:value>', methods=['POST'])
@login_required(api=True)
def rate_post(pid, value):
    resp = {'success': False, 'error': '', 'value': None}
    cuid = session.get('uid', None)
    if cuid is not None:
        if pm.exists(pid):
            lm.rate(pid, cuid, value)
            resp['success'] = True
            resp['value'] = value
        else:
            resp['error'] = 'Публикация не существует'
    else:
        resp['error'] = 'Доступ ограничен'
    return jsonify(resp)


# @api_app.route('/average_rating/<int:pid>', methods=['GET'])
# def average_rating(pid):
#     resp = {'success': False, 'error': '', 'value': None}
#     if pm.exists(pid):
#         resp['success'] = True
#         resp['value'] = lm.average_rating(pid)
#     else:
#         resp['error'] = 'Публикация не существует'
#     return jsonify(resp)


@api_app.route('/post_stats/<int:pid>')
def post_stats(pid):
    resp = {'success': False, 'error': '', 'stats': {}}
    if pm.exists(pid):
        resp['success'] = True
        r = dict()
        r['average_rating'] = lm.average_rating(pid)
        r['comments_number'] = len(cm.find(post_id=pid))
        resp['stats'] = r
    else:
        resp['error'] = 'Публикация не существует'
    return jsonify(resp)
