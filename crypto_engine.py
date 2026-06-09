import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM #It provides for authenticity (detects if the hidden bits have been tampered)
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC #AES requires a 256-bit key, but users will give us a password. PBKDF2 stretches that password into a secure key.
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag #Thrown when the password is wrong or if the data is tampered

class CryptoEngine:
    
    def __init__(self):
        #These sizes are in bytes
        self.SALT_SIZE = 16   #for PBKDF2 key stretching
        self.NONCE_SIZE = 12  #for AES-GCM
        self.KEY_SIZE = 32    #for AES-256

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        #Takes a weak password and stretches it to a strong key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), 
            length=self.KEY_SIZE,
            salt=salt,  #If 2 people use the same password "pass", the salt makes sure that the stretched version is different for both
            iterations=480000, 
        )
        return kdf.derive(password.encode('utf-8'))

    def encrypt_data(self, data: bytes, password: str) -> bytes:
        if not data or not password:
            raise ValueError("Data payload and password cannot be empty.")
        
        salt = os.urandom(self.SALT_SIZE) 
        nonce = os.urandom(self.NONCE_SIZE) #Nonce: Number Used Once
        
        key = self._derive_key(password, salt)

        aesgcm = AESGCM(key)
        
        ciphertext = aesgcm.encrypt(nonce, data, None)

        return salt + nonce + ciphertext    #returns the salt and nonce in plaintext as it is needed for decryption

    def decrypt_data(self, payload: bytes, password: str) -> bytes:
        # A valid package must have at least: 16 bytes (salt) + 12 bytes (nonce) + 16 bytes (AES-GCM auth tag).
        if len(payload) < self.SALT_SIZE + self.NONCE_SIZE + 16:
            raise ValueError("Payload is too small. It may be corrupted or not encrypted.")

        salt = payload[:self.SALT_SIZE]
        nonce = payload[self.SALT_SIZE : self.SALT_SIZE + self.NONCE_SIZE]
        ciphertext = payload[self.SALT_SIZE + self.NONCE_SIZE :]

        key = self._derive_key(password, salt)  #Recreating the same key
        aesgcm = AESGCM(key)
        
        try:
            return aesgcm.decrypt(nonce, ciphertext, None)
        except InvalidTag:
            # If the password is wrong OR if the image compression altered a single bit of our data
            raise ValueError("Decryption failed: Incorrect password or tampered data.")
        
    def encrypt_text(self, text: str, password: str) -> bytes:
        return self.encrypt_data(text.encode('utf-8'), password)

    def decrypt_text(self, payload: bytes, password: str) -> str:
        decrypted_bytes = self.decrypt_data(payload, password)
        try:
            return decrypted_bytes.decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError("Decryption successful, but data is not valid UTF-8 text (might be a binary file).")