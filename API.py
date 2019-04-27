from processing import *
import os
from flask import Blueprint, send_file, request, jsonify, session, current_app
from werkzeug.utils import secure_filename

api_app = Blueprint('API', __name__)


@api_app.route('/image/<ref>')
def image(ref='0'):
    pref = 'static\\img'
    nf = 'image_not_found.png'
    if not ref.isdigit():
        if ref == 'not_found':
            f_name = 'not_found.jpg'
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


@api_app.route('/upload_avatar', methods=['POST'])
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
