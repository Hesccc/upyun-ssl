from flask import render_template

def register_error_handlers(app):
    """注册全局错误处理函数到Flask应用"""

    @app.errorhandler(404)
    def page_not_found(error):
        # 确保模板文件名是 404.html（与你的实际文件名一致）
        return render_template("400.html"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("500.html"), 500