import json
from flask import Blueprint, request, jsonify
from models import logs, upyun, init_db, password

log = logs.configuration()  # 全局初始化日志记录对象
blue_core = Blueprint("blue_core", __name__)  # 创建蓝图

@blue_core.route('/api/webhook', methods=['POST'])
def webhook():
    # 获取 token 参数
    token = request.args.get('token')
    # 获取 headers.type 参数
    type_content = request.headers.get('type')
    # 获取webhook 访问url地址
    url = request.url

    if token == "f8e2c3a4-2ccf-4b57-86fa-027f1e91a5ac":
        log.info(f'[certificate]✌️{token}校验通过!')

        # 处理web页面中的webhook测试请求
        if type_content == 'test':
            log.info(f"[webhook]✌️webhook测试成功,url={url}")
            return jsonify({'status': 'success', 'message': 'Received message successfully'}), 200

        # 处理Certimate 或 其他 webhook 请求
        else:
            # 获取接收到的消息内容
            message = request.json

            # 获取证书内容
            certificate = {
                "certificate": message["cert"],
                "private_key": message["privkey"]
            }

            log.info(f'[certificate]打印证书内容：{str(json.dumps(certificate,ensure_ascii=False))}')

            # 从数据库中获取upyun账号密码
            db = init_db.getDB()
            cloud_user = db.execute('SELECT * FROM cloud_config LIMIT 1;').fetchone()

            if cloud_user:
                # 登录upyun网站获取：Cookies
                cookies = upyun.login(cloud_user[1], password.decrypt_password(cloud_user[2]))

                if cookies is not None:
                    # 将更新的证书内容上传到upyun网站，并返回证书id
                    log.info(f'[certificate]✌️使用{cloud_user[1]},{password.decrypt_password(cloud_user[2])}登录upyun.com网站成功并且成功获取到cookies.')
                    new_certid = upyun.upload_cert(cookies=cookies, certificate=certificate)

                    # 获取正在使用的证书ID
                    log.info("[certificate]Getting the ID of the certificate currently in use from upyun.com")
                    old_certid = upyun.list_cert(cookies=cookies)
                    if old_certid is not None and old_certid != new_certid:
                        log.info(
                            f"[certificate]Starting certificate migration task on upyun.com, old certificate ID: {old_certid} -> new certificate ID: {new_certid}")
                        res = upyun.migrate_cert(old_certid, new_certid, cookies)
                        log.info(f"[certificate]Certificate migration task completed, result: {res}")
                        # 返回响应给发送方
                        return jsonify({'status': 'success', 'message': 'Received message successfully'}), 200
                    else:
                        log.warn(
                            f"[certificate]Certificate migration failed, old certificate ID: {old_certid} is the same as new certificate ID: {new_certid}, skipping migration!")
                        return jsonify({'status': 'failure',
                                        'message': 'Certificate migration failed, old certificate ID: ' + str(
                                            old_certid) + ' is the same as new certificate ID: ' + str(
                                            new_certid) + ' , skipping migration!'}), 200
                else:
                    return jsonify({'status': 'failure', 'message': 'Failed to get cookies'}), 400
            else:
                log.info("[certificate]🙌upyun账号和密码未配置,请在网页中完成配置操作!")

    else:
        log.warn(f'[certificate]🙌{token}校验不通过!')
        return jsonify({'status': 'failure', 'message': 'Token verification does not match'}), 400