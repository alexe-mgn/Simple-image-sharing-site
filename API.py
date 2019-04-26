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
        elif os.path.isfile(os.path.join(pref, ref)):
            f_name = ref
        else:
            f_name = nf
    else:
        img = im.get(int(ref))
        if img is not None:
            f_name = img['filename']
        else:
            f_name = nf
    return send_file(os.path.join(pref, f_name))


@api_app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    data = request.files.get('avatar_image', None)
    a = dir(data)
    if data:
        cuid = session.get('uid', None)
        if cuid is not None:
            img_id = im.upload_secure(data, secure_filename(data.filename))
            if img_id is not None:
                um.edit(cuid, avatar_id=img_id)
                return jsonify({'success': True})
    return jsonify({'success': False})
