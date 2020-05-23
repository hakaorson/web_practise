# 从app模块中即从__init__.py中导入创建的应用
from app import app
from app import db
from app import models
import os
from flask import render_template  # 用于返回html参数
from flask import redirect
from flask import request
from flask import url_for
import zipfile
import shutil

CHINUM_MAP = ['一', '二', '三', '四']


def get_structed_info():
    final_info = []
    chaps = models.Chapter.query.all()
    for c_index, chap in enumerate(chaps):
        temp_chap_info = {'show': '第{}章 '.format(
            CHINUM_MAP[c_index]) + chap.chapname, 'name': chap.chapname, 'desc': chap.chapdesc, 'secs': []}
        secs = chap.secs
        for s_index, sec in enumerate(secs):
            temp_sec_info = {'show': '第{}节 '.format(
                CHINUM_MAP[s_index])+sec.secname.split()[-1], 'name': sec.secname.split()[-1], 'desc': sec.secdesc}
            temp_sec_info['video_path'] = sec.video_path
            temp_sec_info['png_path'] = sec.png_path
            temp_sec_info['ppt_path'] = sec.ppt_path
            temp_chap_info['secs'].append(temp_sec_info)
        final_info.append(temp_chap_info)
    return final_info

# 建立路由，通过路由可以执行其覆盖的方法，可以多个路由指向同一个方法，意思就是给出了/index就执行一次这个方法
@app.route('/')
@app.route('/index')
def route_index():  # 这个index返回的东西就是网页需要呈现的东西，在html中可以使用关键词调用数据
    # 得到介绍信息
    final_info = get_structed_info()
    result = render_template('main/index.html', chaps=final_info)
    return result


@app.route('/media')
@app.route('/media/<chapter>/<section>/videos')
def route_media(chapter=None, section=None):
    final_info = get_structed_info()
    if chapter and section:
        secname = ' '.join([chapter, section])
        query = models.Section.query.filter(
            models.Section.secname == secname).first()
        video_path = query.video_path
        png_path = query.png_path
        if video_path:
            video_path = video_path[4:]  # 替换前面的app/这几个字段
        if png_path:
            pass
        result = render_template(
            'main/media.html', chaps=final_info, video_path=video_path)
    else:
        result = render_template('main/media.html', chaps=final_info)
    return result


@app.route('/file')
@app.route('/file/<type>')
def route_file(type=None):
    final_info = get_structed_info()
    result = render_template('main/file.html', chaps=final_info)
    return result


@app.route('/chart')
def route_chart():
    final_info = get_structed_info()
    result = render_template('main/chart.html', chaps=final_info)
    return result


@app.route('/manage/file', methods=['GET', 'POST'])
def route_manage_file():
    # input_data = request.get_data('homework name')
    if request.form.get('homework name'):
        name = request.form.get('homework name')
        desc = request.form.get('homework desc')
        path = 'files/pdfs/homeworks/{}.pdf'.format(name)
        file = request.files['homework file']
        file.save('app/static/'+path)
        item = models.Homework(name=name, desc=desc, path=path)
        query = models.Homework.query.filter(models.Homework.name == name)
        if query.first():
            query.update({'desc': desc, 'path': path})
        else:
            db.session.add(item)
        db.session.commit()
    if request.form.get('case name'):
        name = request.form.get('case name')
        desc = request.form.get('case desc')
        path = 'files/pdfs/cases/{}.pdf'.format(name)
        file = request.files['case file']
        file.save('app/static/'+path)
        item = models.Case(name=name, desc=desc, path=path)
        query = models.Case.query.filter(models.Case.name == name)
        if query.first():
            query.update({'desc': desc, 'path': path})
        else:
            db.session.add(item)
        db.session.commit()

    homework_infos = []
    for info in models.Homework.query.all():
        url_path = '/static/'+info.path
        homework_infos.append(
            {'name': info.name, 'desc': info.desc, 'path': url_path})
    case_infos = []
    for info in models.Case.query.all():
        url_path = '/static/'+info.path
        case_infos.append(
            {'name': info.name, 'desc': info.desc, 'path': url_path})
    result = render_template(
        'manage/file.html', homework_infos=homework_infos, case_infos=case_infos)
    return result


@app.route('/manage/chapter', methods=['GET', 'POST'])
def route_manage_chapter():
    if request.form.get('chapter input') and request.form.get('chapter name'):
        chapname = request.form.get('chapter name')
        chapdesc = request.form.get('chapter desc')
        all_chapname = [item.chapname for item in models.Chapter.query.all()]
        if chapname not in all_chapname:
            item = models.Chapter(chapname=chapname, chapdesc=chapdesc)
            db.session.add(item)
            db.session.commit()
    if request.form.get('sec input') and request.form.get('sec name') and request.form.get('select chap'):
        secname = request.form.get('sec name')
        chapname = request.form.get('select chap').split()[-1]
        secname = ' '.join([chapname, secname])
        secdesc = request.form.get('sec desc')
        all_name = [item.secname for item in models.Section.query.all()]
        if secname not in all_name:
            item = models.Section(
                secname=secname, chap_=chapname, secdesc=secdesc)
            db.session.add(item)
            db.session.commit()
    final_info = get_structed_info()
    result = render_template('manage/chapter.html', chaps=final_info)
    return result


@app.route('/manage/media', methods=['GET', 'POST'])
def route_manage_media():
    if request.form.get('upload file') and request.form.get('select chap'):
        chap, sec = request.form.get('select chap').split()
        path = os.path.join(
            'app/static', 'files/{}/{}'.format(chap, sec))
        os.makedirs(path, exist_ok=True)

        if request.files['ppt file'].filename:
            query = models.Section.query.filter(
                models.Section.secname == request.form.get('select chap'))
            temp = query.first().ppt_path
            if query.first().ppt_path:
                os.remove(query.first().ppt_path)
            pptfile = request.files['ppt file']
            ppt_path = os.path.join(path, request.files['ppt file'].filename)
            pptfile.save(ppt_path)

            query.update({'ppt_path': ppt_path})
        if request.files['video file']:
            query = models.Section.query.filter(
                models.Section.secname == request.form.get('select chap'))
            if query.first().video_path:
                os.remove(query.first().video_path)
            videofile = request.files['video file']
            video_path = os.path.join(
                path, request.files['video file'].filename)
            videofile.save(video_path)
            query.update({'video_path': video_path})
        if request.files['png file']:
            query = models.Section.query.filter(
                models.Section.secname == request.form.get('select chap'))
            if query.first().png_path:
                shutil.rmtree(query.first().png_path)
                os.remove(query.first().png_path+'.zip')
            pngrarfile = request.files['png file']
            png_path = os.path.join(
                path, pngrarfile.filename)
            pngrarfile.save(png_path)
            zip_file = zipfile.ZipFile(pngrarfile)
            for name in zip_file.namelist():
                zip_file.extract(name, path)
                new_name = name.encode('cp437').decode('gbk')
                os.rename(os.path.join(path, name),
                          os.path.join(path, new_name))  # 防止出现乱码，需要改名
            query.update({'png_path': os.path.join(
                path, pngrarfile.filename[:-4])})
    db.session.commit()
    final_info = get_structed_info()
    result = render_template('manage/media.html', chaps=final_info)
    return result


@app.route('/delete_file/<h_or_c>/<name>')
def delete_file(h_or_c, name):
    if h_or_c == 'homework':
        path = os.path.join(
            os.getcwd(), 'app/static/files/pdfs/homeworks', name+'.pdf')
        if os.path.exists(path):
            os.remove(path)
        query = models.Homework.query.filter(
            models.Homework.name == name).first()
        db.session.delete(query)
        db.session.commit()
        result = redirect(url_for('route_manage_file'))
    else:
        path = os.path.join(
            os.getcwd(), 'app/static/files/pdfs/cases', name+'.pdf')
        if os.path.exists(path):
            os.remove(path)
        query = models.Case.query.filter(
            models.Case.name == name).first()
        db.session.delete(query)
        db.session.commit()
        result = redirect(url_for('route_manage_file'))
    return result


@app.route('/delete_chapter/<chapname>')
@app.route('/delete_chapter/<chapname>/<secname>')
def delete_chapter(chapname, secname=None):
    if secname:
        secname = ' '.join([chapname, secname])
        query = models.Section.query.filter(
            models.Section.secname == secname).first()
        db.session.delete(query)
        db.session.commit()
        result = redirect(url_for('route_manage_chapter'))
    else:
        sec_query = models.Section.query.filter(
            models.Section.chap_ == chapname).all()
        chap_query = models.Chapter.query.filter(
            models.Chapter.chapname == chapname).first()
        for q in sec_query:
            db.session.delete(q)
        db.session.delete(chap_query)
        db.session.commit()
        result = redirect(url_for('route_manage_chapter'))
    return result


@app.route('/clear_media/<choose>/<chapname>/<secname>')
def clear_media(choose, chapname, secname):
    if choose == 'ppt':
        secname = ' '.join([chapname, secname])
        query = models.Section.query.filter(
            models.Section.secname == secname)
        if query.first().ppt_path:
            os.remove(query.first().ppt_path)
        query.update({'ppt_path': ''})
        db.session.commit()
        result = redirect(url_for('route_manage_media'))
    elif choose == 'video':
        secname = ' '.join([chapname, secname])
        query = models.Section.query.filter(
            models.Section.secname == secname)
        if query.first().video_path:
            os.remove(query.first().video_path)
        query.update({'video_path': ''})
        db.session.commit()
        result = redirect(url_for('route_manage_media'))
    else:
        secname = ' '.join([chapname, secname])
        query = models.Section.query.filter(
            models.Section.secname == secname)
        if query.first().png_path:
            shutil.rmtree(query.first().png_path)
            os.remove(query.first().png_path+'.zip')
        query.update({'png_path': ''})
        db.session.commit()
        result = redirect(url_for('route_manage_media'))
    return result
