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
from app.routes import base
from flask_login import login_user, logout_user, login_required, current_user
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired


# 定义的表单都需要继承自FlaskForm
class LoginForm(FlaskForm):
    # 域初始化时，第一个参数是设置label属性的
    username = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
# 建立路由，通过路由可以执行其覆盖的方法，可以多个路由指向同一个方法，意思就是给出了/index就执行一次这个方法


@app.route('/')
@app.route('/index')
def index():  # 这个index返回的东西就是网页需要呈现的东西，在html中可以使用关键词调用数据
    final_info = base.get_structed_info()
    result = render_template('main/index.html', chaps=final_info)
    return result


@app.route('/chart')
def chart():
    final_info = base.get_structed_info()
    base_info = {'chart_path': 'base/chart.png'}
    result = render_template(
        'main/chart.html', chaps=final_info, base=base_info)
    return result


@app.route('/media/<typ>/<chapter>/<section>')
def media(chapter=None, section=None,typ='video'):
    final_info = base.get_structed_info()
    video_infos = {}
    ppt_infos = {}
    cs_id = '-'.join([chapter, section])
    query = models.Section.query.filter(
        models.Section.cs_id == cs_id).first()
    video_path = query.video_path
    png_path = query.png_path
    if video_path:
        video_name = '{}  视频'.format(query.s_name)
        video_infos = {'name': video_name, 'path': base.filepath_process(
            video_path)}  # 替换前面的app/这几个字段
    if png_path:
        ppt_name = '第{}章  第{}节  {}  PPT文件'.format(
            base.CHINUM_MAP[int(chapter)], base.CHINUM_MAP[int(section)], query.s_name)
        ppt_infos = {'name': ppt_name, 'pngs': [],'ppt_path':query.ppt_path}
        imgpath_list = os.listdir(png_path)
        for index, _ in enumerate(imgpath_list):
            temp_path = os.path.join(png_path, '╗├╡╞╞¼{}.PNG'.format(index+1))#这里写得相当粗糙
            png_info = {'path': base.filepath_process(temp_path)}
            png_info['name'] = '第{}页'.format(str(index+1))
            ppt_infos['pngs'].append(png_info)
    title = '第{}章  第{}节  {}'.format(
        base.CHINUM_MAP[int(chapter)], base.CHINUM_MAP[int(section)], query.s_name)
    return render_template(
        'main/media_{}.html'.format(typ), chaps=final_info, video_infos=video_infos, ppt_infos=ppt_infos, title=title)


@app.route('/file/<typ>')
def file(typ):
    final_info = base.get_structed_info()
    file_info = base.get_file_data()
    if typ == 'home':
        return render_template(
            'main/homework.html', chaps=final_info, file=file_info[0])
    elif typ == 'case':
        return render_template(
            'main/case.html', chaps=final_info, file=file_info[1])
    else:
        return redirect(url_for('index'))


@app.route('/login_form')
def login_form():
    form = LoginForm()
    return render_template('main/login.html', form=form)


@app.route('/submit_login_after', methods=['GET', 'POST'])
def submit_login_after():
    form = LoginForm()
    if not form.validate_on_submit():
        return redirect(url_for('login_form'))
    user = models.User.query.filter(
        models.User.user == form.username.data, models.User.passwd == form.password.data).first()
    if user:
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('manage_chapter'))
    else:
        flash('登录错误')
        return redirect(url_for('login_form'))
