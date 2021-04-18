from Crypto.Cipher import AES
from Crypto import Random
from json import dumps, loads
from base64 import b64decode, b64encode

class Encryption():
    def __init__(self, key):
        key = bytes(key, "utf-8")
        self.key = key.decode('unicode-escape').encode('ISO-8859-1')
        
    def encrypt(self, src_str):
        byte_str = dumps(src_str).encode()
        NONCE = Random.get_random_bytes(AES.block_size-1)
        cipher = AES.new(self.key, AES.MODE_OCB, NONCE)
        ciphertxt, MAC = cipher.encrypt_and_digest(byte_str)
        return b64encode(ciphertxt).decode(), NONCE.decode('latin-1'), MAC.decode('latin-1')

    def decrypt(self, en_str, NONCE, MAC):
        ciphertxt = b64decode(en_str)
        cipher = AES.new(self.key , AES.MODE_OCB, NONCE.encode('latin-1'))
        src_str = cipher.decrypt_and_verify(ciphertxt, MAC.encode('latin-1')).decode()
        src_dict = loads(loads(src_str))
        return src_dict