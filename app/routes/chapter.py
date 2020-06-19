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
CHINUM_MAP = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']


@app.route('/manage/chapter')
@login_required
def manage_chapter():
    final_info = base.get_structed_info()
    result = render_template('manage/chapter.html', chaps=final_info)
    return result


@app.route('/add_chapter', methods=['POST'])
@login_required
def add_chapter():
    chapname = request.form.get('chapname')
    chapdesc = request.form.get('chapdesc')
    all_chap_items = models.Chapter.query.all()
    if chapname and chapname not in [item.c_name for item in all_chap_items]:
        item = models.Chapter(c_id=len(all_chap_items)+1,
                              c_name=chapname, c_desc=chapdesc)
        db.session.add(item)
        db.session.commit()
    return redirect(url_for('manage_chapter'))


@app.route('/add_section/<c_id>', methods=['POST'])
@login_required
def add_section(c_id):
    secname = request.form.get('secname_{}'.format(c_id))
    secdesc = request.form.get('secdesc_{}'.format(c_id))
    all_sec_items = models.Section.query.filter(
        models.Section._chap == c_id).all()
    if secname and secname not in [item.s_name for item in all_sec_items]:
        item = models.Section(
            cs_id=str(c_id) + '-' + str(len(all_sec_items)+1),
            s_name=secname,
            s_desc=secdesc,
            _chap=c_id
        )
        db.session.add(item)
        db.session.commit()
    return redirect(url_for('manage_chapter'))


@app.route('/update_chapter/<c_id>', methods=['POST'])
@login_required
def update_chapter(c_id):
    query = models.Chapter.query.filter(models.Chapter.c_id == c_id)
    chapname = request.form.get('chapname_{}'.format(c_id))
    chapdesc = request.form.get('chapdesc_{}'.format(c_id))
    if chapname:
        query.update({'c_name': chapname})
    if chapdesc:
        query.update({'c_desc': chapdesc})
    db.session.commit()
    return redirect(url_for('manage_chapter'))


@app.route('/update_section/<c_id>/<s_id>', methods=['POST'])
@login_required
def update_section(c_id, s_id):
    query = models.Section.query.filter(
        models.Section.cs_id == '-'.join([c_id, s_id]))
    secname = request.form.get('secname_{}_{}'.format(c_id, s_id))
    secdesc = request.form.get('secdesc_{}_{}'.format(c_id, s_id))
    if secname:
        query.update({'s_name': secname})
    if secdesc:
        query.update({'s_desc': secdesc})
    db.session.commit()
    return redirect(url_for('manage_chapter'))


@app.route('/delete_chapter/<c_id>')
@login_required
def delete_chapter(c_id):
    query = models.Chapter.query.all()
    need_to_change = []
    for item in query:
        item_c_id = int(item.c_id)
        if item_c_id > int(c_id):
            need_to_change.append(item_c_id)
        elif item_c_id == int(c_id):
            s_query = models.Section.query.filter(
                models.Section._chap == c_id).all()
            path = os.path.join(
                'app/static', 'files/{}'.format(c_id))
            if os.path.exists(path):
                shutil.rmtree(path)
            for s_item in s_query:
                db.session.delete(s_item)
            db.session.delete(item)
            if os.path.exists(path):
                shutil.rmtree(path)
        else:
            pass
    sorted(need_to_change)
    for c_id in need_to_change:
        temp_q = models.Chapter.query.filter(
            models.Chapter.c_id == str(c_id))
        temp_q.update({'c_id': str(c_id-1)})
        old_path = os.path.join('app/static', 'files/{}'.format(c_id))
        new_path = os.path.join('app/static', 'files/{}'.format(c_id-1))
        os.rename(old_path, new_path)
    db.session.commit()
    return redirect(url_for('manage_chapter'))


@app.route('/delete_section/<c_id>/<s_id>')
@login_required
def delete_section(c_id, s_id):
    query = models.Section.query.filter(models.Section._chap == c_id).all()
    need_to_change = []
    for item in query:
        item_s_id = int(item.cs_id.split('-')[-1])
        if item_s_id > int(s_id):
            need_to_change.append(item_s_id)
        elif item_s_id == int(s_id):
            path = os.path.join(
                'app/static', 'files/{}/{}'.format(c_id, s_id))
            if os.path.exists(path):
                shutil.rmtree(path)
            db.session.delete(item)
        else:
            pass
    sorted(need_to_change)
    for s_id in need_to_change:
        temp_q = models.Section.query.filter(
            models.Section.cs_id == '-'.join([c_id, str(s_id)]))
        temp_q.update({'cs_id': '-'.join([c_id, str(s_id-1)])})
        old_path = os.path.join('app/static', 'files/{}/{}'.format(c_id, s_id))
        new_path = os.path.join(
            'app/static', 'files/{}/{}'.format(c_id, s_id-1))
        os.rename(old_path, new_path)
    db.session.commit()
    return redirect(url_for('manage_chapter'))
