# 从app模块中即从__init__.py中导入创建的应用
from app import app
from app import db
from app import models
import os
from flask import render_template  # 用于返回html参数
from flask import redirect
from flask import request
from flask_login import login_required
from flask import url_for
from app.routes import base
import zipfile
import shutil
CHINUM_MAP = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']


@app.route('/manage/file')
@login_required
def manage_file():
    final_info = base.get_file_data()
    result = render_template('manage/file.html', files=final_info)
    return result


def add_file_proces(name, typ, file, desc):
    query = models.HomeAndCase.query.filter(
        models.HomeAndCase.name == name)
    path = os.path.join('app/static/{}/{}'.format(typ, name))
    if len(query.all()) == 0:
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, file.filename)
        file.save(file_path)
        db.session.add(models.HomeAndCase(
            name=name, desc=desc, path=file_path, typ=typ, file=file.filename))


@app.route('/add_file/<typ>', methods=['GET', 'POST'])
@login_required
def add_file(typ):
    if request.form.get('name'):
        name = request.form.get('name')
        desc = request.form.get('desc')
        try:
            file = request.files['file']
            add_file_proces(name, typ, file, desc)
            db.session.commit()
            return redirect(url_for('manage_file'))
        except Exception:
            return redirect(url_for('manage_file'))
    else:
        return redirect(url_for('manage_file'))


@app.route('/delete_file/<typ>/<name>', methods=['GET', 'POST'])
@login_required
def delete_file(typ, name):
    query = models.HomeAndCase.query.filter(
        models.HomeAndCase.name == name).first()
    father_director = os.path.join('app/static/{}/{}'.format(typ, name))
    if os.path.exists(father_director):
        shutil.rmtree(father_director)
    db.session.delete(query)
    db.session.commit()
    return redirect(url_for('manage_file'))


@app.route('/update_file/<typ>/<name>', methods=['GET', 'POST'])
@login_required
def update_file(typ, name):
    newname = request.form.get('name')
    newdesc = request.form.get('desc')
    director = os.path.join('app/static/{}/{}'.format(typ, name))
    if request.files['file'].filename:
        if os.path.exists(director):
            shutil.rmtree(director)
        query = models.HomeAndCase.query.filter(
            models.HomeAndCase.name == name).first()
        db.session.delete(query)
        newname = newname if newname else query.name
        newdesc = newdesc if newdesc else query.desc
        add_file_proces(newname, typ, request.files['file'], newdesc)
        db.session.commit()
        return redirect(url_for('manage_file'))
    else:
        query = models.HomeAndCase.query.filter(
            models.HomeAndCase.name == name)
        all_names = [item.name for item in models.HomeAndCase.query.all()]
        update_data = {}
        if newname and newname != name and newname not in set(all_names):
            new_director = os.path.join(
                'app/static/{}/{}'.format(typ, newname))
            os.rename(director, new_director)
            update_data['path'] = query.first().path.replace(
                '/{}'.format(name), '/{}'.format(newname))
            update_data['name'] = newname
        if newdesc:
            update_data['desc'] = newdesc
        if update_data:
            query.update(update_data)
            db.session.commit()
        return redirect(url_for('manage_file'))
