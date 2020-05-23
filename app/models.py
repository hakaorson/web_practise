# 完成模型映射
from app import db
from flask_sqlalchemy import SQLAlchemy


class Chapter(db.Model):
    chapname = db.Column(db.String(12), primary_key=True)
    chapdesc=db.Column(db.String(12))
    # 这是调用，可以定位条目而不是值
    secs = db.relationship('Section', backref='chap')


class Section(db.Model):
    secname = db.Column(db.String(12), primary_key=True)
    secdesc=db.Column(db.String(12))
    # 这只是约束
    chap_ = db.Column(db.String(12), db.ForeignKey(Chapter.chapname))
    ppt_path = db.Column(db.String(24))
    png_path=db.Column(db.String(24))
    video_path = db.Column(db.String(24))


class Homework(db.Model):
    name = db.Column(db.String(12), primary_key=True)
    desc = db.Column(db.String(32))
    path = db.Column(db.String(24))


class Case(db.Model):
    name = db.Column(db.String(12), primary_key=True)
    desc = db.Column(db.String(32))
    path = db.Column(db.String(24))


db.create_all()  # 创建所有的表，已经存在的表不会再次创建
