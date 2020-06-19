from flask import Flask  # 导入Flask包

app = Flask(__name__)  # 获取Flask对象，以当前模块名为参数

# 路由默认为（127.0.0.1:5000）
@app.route('/')  # 装饰器对该方法进行路由设置，请求的地址
def hello_world():  # 方法名称
    return 'Hello     World! '  # 返回响应的内容


if __name__ == '__main__':
    app.run()
