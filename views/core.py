import json
from flask import Blueprint, request, jsonify
from models import logs, upyun

log = logs.configuration()  # 全局初始化日志记录对象
blue_core = Blueprint("blue_core", __name__)  # 创建蓝图

@blue_core.route('/api/webhook', methods=['POST','GET'])
def webhook():
    type_content = request.headers.get('type')
    url = request.url

    if type_content == 'test':
        log.warn(f"[Webhook Test]✌️用户进行webhook测试成功,url:{url}")
        return jsonify({'status': 'success', 'message': 'Received message successfully'}), 200
    else:
        # 获取接收到的消息内容
        message = request.json
        log.info("Received webhook request: " + json.dumps(message, ensure_ascii=False))
        certificate = {
            "certificate": message["cert"],
            "private_key": message["privkey"]
        }

        # 登录upyun网站获取：Cookies
        log.info("Attempting to log in to upyun.com to get cookies")
        cookies = upyun.login(username, password)

        if cookies is not None:
            # 将更新的证书内容上传到upyun网站，并返回证书id
            log.info("Starting to upload certificate to upyun.com, certificate content: " + json.dumps(certificate, ensure_ascii=False))
            new_certid = upyun.upload_cert(cookies=cookies, certificate=certificate)

            # 获取正在使用的证书ID
            log.info("Getting the ID of the certificate currently in use from upyun.com")
            old_certid = upyun.list_cert(cookies=cookies)
            if old_certid is not None and old_certid != new_certid:
                log.info(f"Starting certificate migration task on upyun.com, old certificate ID: {old_certid} -> new certificate ID: {new_certid}")
                res = upyun.migrate_cert(old_certid, new_certid, cookies)
                log.info(f"Certificate migration task completed, result: {res}")
                # 返回响应给发送方
                return jsonify({'status': 'success', 'message': 'Received message successfully'}), 200
            else:
                log.error(f"Certificate migration failed, old certificate ID: {old_certid} is the same as new certificate ID: {new_certid}, skipping migration!")
                return jsonify({'status': 'failure', 'message': 'Certificate migration failed, old certificate ID: '+ str(old_certid) +' is the same as new certificate ID: '+ str(new_certid) +' , skipping migration!'}), 200
        else:
            return jsonify({'status': 'failure','message': 'Failed to get cookies'}),400