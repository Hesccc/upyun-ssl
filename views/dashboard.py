from flask import Blueprint, render_template, request, url_for, redirect, jsonify, session
from tools.authcheck import auth
from tools.initDB import getDB
from tools.password import encrypt_password, decrypt_password
from werkzeug.security import generate_password_hash, check_password_hash
import socket

from models import upyun, logs
# 全局初始化日志记录对象
log = logs.configuration()
blue_dashboard = Blueprint("blue_dashboard", __name__)  # 创建蓝图

# 应用配置界面
@blue_dashboard.route('/dashboard', methods=['GET'])
@auth
def dashboard():
    db = getDB()  # 获取数据对象
    user = db.execute('SELECT * FROM cloud_config LIMIT 1;').fetchone()  # 搜索数据库，获取账号密码
    db.commit()  # 提交数据库操作
    return render_template("dashboard.html",username=user[1], password=decrypt_password(user[2]))


@blue_dashboard.route('/account/save', methods=['POST','GET'])
@auth
def account_save():
    if request.method == "GET":
        return redirect(url_for("/"))

    elif request.method == "POST":
        cloud_user = request.form.get('username')
        cloud_passwd = request.form.get('password')

        db = getDB()  # 获取数据对象
        user = db.execute('SELECT * FROM cloud_config WHERE cloud_user = ?', (cloud_user,)).fetchone()  # 搜索数据库，判断用户输入的账号密码是否存在
        db.commit()  # 提交数据库操作
        if user and decrypt_password(user[2]) == cloud_passwd:  # 验证账号密码是否已保存
            log.warn(f"[账号检查]账号已经存在!请勿重复保存:username={str(cloud_user)},password={str(cloud_passwd)}")
            return render_template("dashboard.html", username=cloud_user, password=cloud_passwd, testMsg="🙌保存失败!账号已经存在，请勿重复保存!")  # 条件符合时，提示账号密码已保存

        # 账号密码不存在，进行下一步
        else:
            cookies = upyun.login(cloud_user, cloud_passwd)
            if cookies is not None:
                db.execute('INSERT INTO cloud_config (cloud_user, cloud_pass) VALUES (?, ?)',[cloud_user, encrypt_password(cloud_passwd)])  # 插入新账号密码
                db.commit()  # 提交数据库操作
    
                log.info(f"[保存账号]保存账号成功!成功获取cookies={str(cookies)}")
                return render_template("dashboard.html", username=cloud_user, password=cloud_passwd, testMsg="✌️登录测试成功，账号密码保存成功!")
            else:
                log.warn(f"[保存账号]保存账号失败!账号和密码输入有误,请检查:username={str(cloud_user)},password={str(cloud_passwd)}")
                return render_template("dashboard.html", username=cloud_user, password=cloud_passwd, testMsg="🙌登录测试失败!账号密码未保存，👀请检查账号密码!")


@blue_dashboard.route('/account/test', methods=['POST','GET'])
@auth
def account_test():
    if request.method == "GET":
        return redirect(url_for("/"))

    elif request.method == "POST":
        cloud_user = request.form.get('username')
        cloud_passwd = request.form.get('password')
        cookies = upyun.login(cloud_user, cloud_passwd)
        if cookies is not None:
            log.info(f"[测试登录]✌️使用username={cloud_user},password={cloud_passwd},登录upyun.com成功!")
            return render_template("dashboard.html", username=cloud_user, password=cloud_passwd, testMsg="✌️登录成功，测试通过!")
        else:
            log.info(f"[测试登录]🙌使用username={cloud_user},password={cloud_passwd},登录upyun.com失败!")
            return render_template("dashboard.html", username=cloud_user, password=cloud_passwd, testMsg="🙌登录失败，测试不通过!")


@blue_dashboard.route('/api/ShowLogs', methods=['POST','GET'])
@auth
def ShowLogs():
    try:
        with open('log/upyun.log', 'r', encoding='utf-8') as f:
            logs = f.readlines()

        log.info(f"[查看日志]✌️查看日志成功!")
        return jsonify({'status': 'success', 'logs': logs})   
    except Exception as e:
        log.warn(f"[查看日志]🙌打开日志文件失败!")
        return jsonify({'status': 'error', 'message': str(e)})


# 修改密码接口
@blue_dashboard.route('/api/ChangePasswd', methods=['POST','GET'])
@auth
def change_password():
    if request.method == 'GET':
        return redirect(url_for('/'))

    elif request.method == 'POST':
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        if not old_password or not new_password:
            log.info(f"[修改密码]🙌修改密码失败,密码不能为空!")
            return jsonify({'success': False, 'message': '🙌密码不能为空!'})

        db = getDB()  # 获取数据对象
        user = db.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()  # 搜索数据库，判断用户输入的账号密码是否存在

        if user and check_password_hash(user[2], old_password):
            db.execute('UPDATE users SET password = ? WHERE username = ?', (generate_password_hash(new_password), session['username']))  # 更新密码
            db.commit()  # 提交数据库操作
            session.clear()  # 清理session
            log.info(f"[修改密码]✌️修改密码成功!")
            return jsonify({'success': True})
        else:
            log.warn(f"[修改密码]🙌修改密码失败,当前密码错误:{old_password}")
            return jsonify({'success': False, 'message': '🙌当前密码错误!'})


# webhooks接口信息
@blue_dashboard.route('/api/WebhookInfo', methods=['GET'])
@auth
def WebhookInfo():
    try:
        # 获取服务器的IP地址
        hostname = socket.gethostname()
        server_ip = socket.gethostbyname(hostname)

        # 获取Flask运行的端口
        server_port = request.host.split(':')[1]
        # 生成一个随机的token
        token = 'f8e2c3a4-2ccf-4b57-86fa-027f1e91a5ac'
        webhook_url = f"http://{server_ip}:{server_port}/api/webhook?token={token}"

        log.info(f"[webhook]✌️获取Webhook信息成功: {webhook_url}")

        return jsonify({'success': True, 'webhook_url': webhook_url})
    except Exception as e:
        log.warn(f"[webhook]🙌获取Webhook信息失败!: {str(e)}")

        return jsonify({'success': False, 'message': str(e)})