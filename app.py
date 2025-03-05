import os
from flask import Flask
from datetime import timedelta
from models.init_db import init_db  # 导入数据库初始化函数

from views.login import blue_auth
from views.dashboard import blue_dashboard
from views.error import register_error_handlers
from views.core import blue_core

# 创建一个Flask应用，并指定静态文件夹
app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # 设置会话有效期

# 注册数据库
db = init_db(app)

# 注册错误处理器
register_error_handlers(app)

app.register_blueprint(blueprint=blue_auth)  # 登录蓝图
app.register_blueprint(blueprint=blue_dashboard)  # 管理配置蓝图
app.register_blueprint(blueprint=blue_core)  # 核心功能蓝图

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')