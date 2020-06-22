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
CHINUM_MAP = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二',
              '十三', '十四', '十五', '十六', '十七', '十八']


def filepath_process(path):  # 获取到file文件的路径
    if path:
        path = path.replace('\\', '/')
        path_list = path.split('/')
        result = '/'.join(path_list[2:])
        return result
    else:
        return None


def get_structed_info():
    final_info = []
    chaps = models.Chapter.query.all()
    for chap in chaps:
        c_id = int(chap.c_id)
        temp_chap_info = {
            'c_id': c_id,
            'c_index': '第{}章 '.format(CHINUM_MAP[c_id]),
            'name': chap.c_name,
            'desc': chap.c_desc,
            'secs': []
        }
        secs = chap.secs
        for sec in secs:
            s_id = int(sec.cs_id.split('-')[-1])
            meida_datas = []
            meida_datas.append({
                'type': 'ppt', 'exit': 'true'if sec.ppt_path else None, 'path': filepath_process(sec.ppt_path)})
            meida_datas.append({
                'type': 'png', 'exit': 'true'if sec.png_path else None, 'path': filepath_process(sec.png_path)})
            # print(filepath_process(sec.png_path))
            meida_datas.append({
                'type': 'video', 'exit': 'true'if sec.video_path else None, 'path': filepath_process(sec.video_path)})
            temp_sec_info = {
                's_id': s_id,
                's_index': '第{}节 '.format(CHINUM_MAP[s_id]),
                'name': sec.s_name,
                'desc': sec.s_desc,
                'c_s_index': '第{}章 第{}节'.format(CHINUM_MAP[c_id], CHINUM_MAP[s_id]),
                'media_data': meida_datas
            }
            temp_chap_info['secs'].append(temp_sec_info)
        final_info.append(temp_chap_info)
    return final_info


def get_file_data():
    types = ['home', 'case']
    finale_info = [{'typ': types[0], 'desc': '作业', 'list': []},
                   {'typ': types[1], 'desc': '案例', 'list': []}]
    for info in models.HomeAndCase.query.all():
        data = {'name': info.name, 'desc': info.desc,
                'path': filepath_process(info.path),
                'file': info.file
                }
        finale_info[types.index(info.typ)]['list'].append(data)
    return finale_info
