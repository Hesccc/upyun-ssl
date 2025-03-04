from flask import g
from werkzeug.security import generate_password_hash
from models import logs   # 加载日志模型
import sqlite3

log = logs.configuration()  # 全局初始化日志记录对象

DATABASE = 'db/database.db'  # 设置数据库文件
SQLFILE = 'db/schema.sql'    # 设置初始化SQL文件

# 数据库初始化
def init_db(app):
    with app.app_context():
        db = getDB()
        # 执行建表语句（schema.sql）
        with app.open_resource(SQLFILE, mode='rb') as f:
            content = f.read().decode('utf-8')
            db.cursor().executescript(content)

        # 插入初始数据前检查是否存在
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', ['admin'])
        if not cursor.fetchone():
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',['admin', generate_password_hash('admin@123')])

        log.info(f"[初始化数据库]✌️初始化数据库完成!")
        db.commit()
    return db


# 获取数据库信息
def getDB():
    db = getattr(g, '_database', None)
    if db is None:
        log.info(f"[初始化数据库]✌️创建或加载数据库文件成功.")
        db = g._database = sqlite3.connect(DATABASE)
    return db