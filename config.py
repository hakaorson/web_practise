import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
#需要预先安装好目录

class Config(object):
    # 格式为mysql+pymysql://数据库用户名:密码@数据库地址:端口号/数据库的名字?数据库格式
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://hakaorson:GP361361@rm-2ze5jv50a270u26329o.mysql.rds.aliyuncs.com:3306/teachweb_database?charset=UTF8MB4'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(BASE_DIR, 'teach_web.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
