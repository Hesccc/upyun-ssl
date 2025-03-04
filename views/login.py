from flask import Blueprint, render_template, request, session, url_for, redirect
from tools.authcheck import auth, generate_session_id
from tools.initDB import getDB
from werkzeug.security import check_password_hash

from models import logs   # 加载日志模型
log = logs.configuration()  # 全局初始化日志记录对象

blue_auth = Blueprint("blue_auth", __name__)

# 登录
@blue_auth.route('/')
@blue_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
        
    elif request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        # 登录判断逻辑
        db = getDB()  # 获取数据对象
        user = db.execute('SELECT id,username,password FROM users WHERE username = ?', (username,)).fetchone()  # 搜索数据库，判断用户输入的账号密码是否存在
        if user and check_password_hash(user[2], password):
            # 验证用户名密码成功后
            session['username'] = username
            session['session_id'] = generate_session_id()
            session['user_ip'] = request.remote_addr
            session['user_agent'] = request.headers.get('User-Agent')
            session.permanent = True  # 启用持久会话（可选）
            log.info(f"[登录]✌️用户登录成功:username={username},session_id={session['session_id']}")
            return redirect(url_for('blue_dashboard.dashboard'))
        else:
            log.warn(f"[登录]🙌用户登录失败:username={username},password={password}")
            return render_template("login.html", loginMSG="账号或密码错误！")

# 账号登出
@blue_auth.route('/logout')
@auth
def logout():
    session.clear()
    session.modified = True  # 标记会话为已修改
    response = redirect(url_for('blue_auth.login'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response