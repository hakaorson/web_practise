# 从app模块中导入应用
from app import app  # 这个应用在app中走了一轮，可以使用run方法直接启用


# 防止被引用后执行，只有在当前模块中才可以使用
if __name__ == '__main__':
    app.run(debug=True)  # 这个需要和阿里云服务器一致
