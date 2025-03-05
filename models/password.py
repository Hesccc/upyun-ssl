from cryptography.fernet import Fernet
import base64

# 原始密钥（32字节的字符串）
original_key = "EyrtaEDwHACkh6SdbHdcT7PcAswJmGHR"

# 将原始密钥转换为字节并进行base64编码
key_bytes = original_key.encode()  # 32字节的原始数据
fernet_key = base64.urlsafe_b64encode(key_bytes).decode()  # 生成44字符的base64密钥

# 使用正确的密钥初始化Fernet
fernet = Fernet(fernet_key)

def encrypt_password(password: str) -> str:
    """加密密码并返回字符串"""
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    """解密密码返回明文"""
    return fernet.decrypt(encrypted_password.encode()).decode()