from models import logs
import json, requests

# 全局初始化日志记录对象
log = logs.configuration()


# 使用账号密码登录，获取cookies
def login(username: str, password: str):
    url = "https://console.upyun.com/accounts/signin/"  # 登录接口url
    session = requests.Session()  # 创建一个session对象
    # 创建请求头 By headers
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://console.upyun.com',
        'priority': 'u=1, i',
        'referer': 'https://console.upyun.com/login/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    # 登录的账号和密码
    user = {
        'username': username,
        'password': password,
    }

    try:
        response = session.post(url=url, headers=headers, json=user).json()

        # 判断返回的内容是否为正常登录返回的结果
        if response['data']['result']:
            cookies = session.cookies.get_dict()
            log.info("[upyun]✌️Successfully logged in to upyun.com! Retrieved cookies: " + json.dumps(cookies, ensure_ascii=False))
            return cookies
        else:
            log.info("Failed to log in to upyun.com! No cookies retrieved, returning None. Reason for failure: " + json.dumps(response, ensure_ascii=False))
            return None
    except Exception as e:
        log.error(e)


# 上传证书
def upload_cert(cookies: dict, certificate:dict):
    url = "https://console.upyun.com/api/https/certificate/"
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://console.upyun.com',
        'priority': 'u=1, i',
        'referer': 'https://console.upyun.com/toolbox/ssl/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }
    try:
        # 上传证书内容
        response = requests.post(url=url, cookies=cookies, headers=headers, json=certificate).json()
        log.info("[upyun]✌️Certificate successfully uploaded, certificate ID: " + response['data']['result']['certificate_id'])
        # 返回证书ID
        return response['data']['result']['certificate_id']

    except Exception as e:
        log.error(e)


# 迁移证书
def migrate_cert(old_certid: str, new_certid: str, cookies: dict):
    url = 'https://console.upyun.com/api/https/migrate/certificate'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://console.upyun.com',
        'priority': 'u=1, i',
        'referer': 'https://console.upyun.com/toolbox/ssl/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }

    migrate_certificate = {
        'old_crt_id': old_certid,
        'new_crt_id': new_certid,
    }

    response = requests.post(url, cookies=cookies, headers=headers, json=migrate_certificate).json()
    return response


# 获取证书列表，检索到正在使用的证书ID
def list_cert(cookies: dict):
    url = 'https://console.upyun.com/api/https/certificate/list/'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i',
        'referer': 'https://console.upyun.com/toolbox/ssl/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    }
    params = {'limit': '10',}
    try:
        response = requests.get(url, params=params, cookies=cookies,headers=headers).json()
        # 提取符合条件的对象
        filtered_items = [
            (key, item) for key, item in response["data"]["result"].items()
            # 过滤条件为config_domain > 0 并且 key != default
            if item.get('config_domain', 0) > 0 and key != 'default'
        ]

        if filtered_items:
            # 找到拥有最小过期时间的项，最小过期时间的项为old证书。
            min_end_date_item = min(filtered_items, key=lambda x: x[1].get('validity', {}).get('end', 0))
            old_certid = min_end_date_item[0]
            log.info("[upyun]✌️Successfully retrieved the ID of the certificate in use, certificate ID: " + str(old_certid))
            return old_certid
        else:
            log.error("[upyun]🙌Failed to retrieve the ID of the certificate in use! Please check the configuration on upyun.com")
            return None
    except Exception as e:
        log.error(e)