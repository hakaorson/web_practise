# 从app模块中导入应用
from app import app  # 这个应用在app中走了一轮，可以使用run方法直接启用
from gevent import monkey
from gevent import pywsgi
monkey.patch_all()  # 打上猴子补丁


# 防止被引用后执行，只有在当前模块中才可以使用
if __name__ == '__main__':
    app.debug = True
    server = pywsgi.WSGIServer(('0.0.0.0', 80), app)
    server.serve_forever()
