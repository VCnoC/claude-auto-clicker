"""
密码加密工具模块
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PasswordEncryption:
    """密码加密和解密类"""
    
    def __init__(self, master_key: str = None):
        """
        初始化加密器
        :param master_key: 主密钥，如果为空则使用机器唯一标识生成
        """
        if master_key is None:
            master_key = self._generate_machine_key()
        
        self.key = self._derive_key(master_key)
        self.cipher = Fernet(self.key)
    
    def _generate_machine_key(self) -> str:
        """生成基于机器的唯一密钥"""
        import platform
        import socket
        
        # 使用机器名和用户名组合
        machine_info = f"{platform.node()}-{os.getenv('USER', 'default')}"
        return machine_info
    
    def _derive_key(self, password: str) -> bytes:
        """从密码派生加密密钥"""
        password_bytes = password.encode()
        salt = b'claude_auto_clicker_salt_2024'  # 固定盐值
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """加密明文密码"""
        if not plaintext:
            return ""
        
        encrypted = self.cipher.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """解密密码"""
        if not ciphertext:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            raise ValueError("无法解密密码，可能是密钥不匹配")