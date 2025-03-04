from functools import wraps
from flask import session, redirect, url_for, request, make_response
import secrets

# 生成高强度会话 ID
def generate_session_id():
    return secrets.token_urlsafe(32)

# 会话验证装饰器
def auth(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # 检查关键会话字段
        username = session.get("username")
        session_id = session.get("session_id")
        stored_ip = session.get("user_ip")
        stored_ua = session.get("user_agent")
        
        # 验证逻辑
        is_valid = (
            username
            and session_id
            and stored_ip == request.remote_addr
            and stored_ua == request.headers.get('User-Agent')
            # and validate_session_id(username, session_id)  # 自定义会话验证函数
        )
        
        if not is_valid:
            session.clear()
            return redirect(url_for('blue_auth.login'))
        
        # 执行视图并添加缓存控制头
        response = make_response(func(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        return response
    return decorated_view