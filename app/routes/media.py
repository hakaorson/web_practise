# 从app模块中即从__init__.py中导入创建的应用
from app import app
from app import db
from app import models
import os
from flask import render_template  # 用于返回html参数
from flask import redirect
from flask import request
from flask import url_for
from flask_login import login_required
from app.routes import base
import zipfile
import shutil


@app.route('/manage/media')
@login_required
def manage_media():
    final_info = base.get_structed_info()
    result = render_template('manage/media.html', chaps=final_info)
    return result


def store_request_file(path, name, req_file):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, name)
    req_file.save(file_path)
    if zipfile.is_zipfile(file_path) and file_path[-4:] == '.zip':
        return extract_zip(path, name)
    return os.path.join(path, name)


def extract_zip(path, name):
    file_path = os.path.join(path, name)
    zip_file = zipfile.ZipFile(file_path, "r")
    zip_file.extractall(path)
    return file_path.replace('.zip', '')


@app.route('/add_media_file', methods=['GET', 'POST'])
@login_required
def add_media_file():
    file_list = {'ppt_file': None, 'video_file': None, 'png_file': None}
    if not request.form.get('select chap'):
        return redirect(url_for('manage_media'))
    chap, sec = request.form.get('select chap').split()
    path = os.path.join('app/static', 'files/{}/{}'.format(chap, sec))
    update_data = {}
    for file_type in file_list.keys():
        request_file = request.files[file_type]
        file_list[file_type] = request_file
        if request_file.filename:
            update_path = os.path.join(path, file_type)
            final_path = store_request_file(
                update_path, request_file.filename, request_file)
            update_data[file_type.replace('file', 'path')] = final_path
    query = models.Section.query.filter(models.Section.cs_id == chap+'-'+sec)
    query.update(update_data)
    db.session.commit()
    return redirect(url_for('manage_media'))


def delete_media_file(c_name, s_name, file_type):
    path = os.path.join(
        'app/static', 'files/{}/{}/{}'.format(c_name, s_name, file_type+'_file'))
    if os.path.exists(path):
        shutil.rmtree(path)
    query = models.Section.query.filter(
        models.Section.cs_id == c_name+'-'+s_name)
    query.update({file_type+'_path': None})
    db.session.commit()


@app.route('/clear_media_file/<c_name>/<s_name>/<file_type>')
@login_required
def clear_media_file(c_name, s_name, file_type):
    delete_media_file(c_name, s_name, file_type)
    return redirect(url_for('manage_media'))
