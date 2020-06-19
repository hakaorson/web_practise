# 完成模型映射
from app import db
from app import login
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


class Chapter(db.Model):
    c_id = db.Column(db.String(64), primary_key=True)
    c_name = db.Column(db.String(64))
    c_desc = db.Column(db.String(64))
    # 这是调用，可以定位条目而不是值
    secs = db.relationship('Section', backref='chap')


class Section(db.Model):
    cs_id = db.Column(db.String(64), primary_key=True)
    s_name = db.Column(db.String(64))
    s_desc = db.Column(db.String(64))
    _chap = db.Column(db.String(64), db.ForeignKey(Chapter.c_id))

    ppt_path = db.Column(db.String(64))
    png_path = db.Column(db.String(64))
    video_path = db.Column(db.String(64))


class HomeAndCase(db.Model):
    name = db.Column(db.String(64), primary_key=True)
    desc = db.Column(db.String(64))
    path = db.Column(db.String(64))
    typ = db.Column(db.String(64))
    file = db.Column(db.String(64))


class User(db.Model):
    user = db.Column(db.String(64), primary_key=True)
    passwd = db.Column(db.String(64))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user


@login.user_loader
def load_user(name):
    return User.query.get(name)


db.create_all()  # 创建所有的表，已经存在的表不会再次创建


def register_temp():
    if User.query.filter(User.user == 'sunlijun').first():
        pass
    else:
        db.session.add(User(user='sunlijun', passwd='888sunlijun'))
        db.session.commit()


register_temp()
