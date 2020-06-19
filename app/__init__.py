# 这个包被导入的时候会执行的程序
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
app = Flask(__name__)  # 注意flask需要根据这个名字去找文件，比如templates,static
login = LoginManager(app)
app.config.from_object(Config)  # 使用函数做配置

app.secret_key = 'hakaorson'
# 添加数据库链接
db = SQLAlchemy(app)
# 进一步简化操作
migrage = Migrate(app, db)

from app import models  # 完成映射
from app.routes import routes  # 需要先有app才能保证routes的运行
from app.routes import chapter
from app.routes import media
from app.routes import file