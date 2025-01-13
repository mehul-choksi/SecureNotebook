import json

from cryptography.fernet import Fernet

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import base64
import re

class FileStorage():

    def __init__(self, file_path=None):
        self.file_path = file_path  # Path will be set dynamically if not provided
        self.content_dict = {}
        self.safe_copy = ''
        self.passphrase = None
        self.encryptionModule = None # default, will be overwritten if initialize is invoked in NotebookManager

    def set_file_path(self, file_path):
        """Set the file path dynamically if not set during initialization."""
        self.file_path = file_path
        

    def initialize(self, passphrase=None):
        self.passphrase = passphrase
        if self.passphrase:
            key = self.generate_fernet_key_from_password(self.passphrase)
            self.encryptionModule = Fernet(key)
        else:
            self.encryptionModule = None
            

    def generate_fernet_key_from_password(self,passphrase):
        password_bytes = passphrase.encode()
        salt = b"RandomSalt"

        # Define the number of iterations for the KDF
        iterations = 100_000

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # Key length for Fernet is 32 bytes
            salt=salt,
            iterations=iterations
        )

        key = kdf.derive(password_bytes)
        fernet_key = base64.urlsafe_b64encode(key)

        return fernet_key
    
    def reset_storage(self):
        """Reset the file storage to remove encryption settings."""
        self.passphrase = None
        self.encryptionModule = None
        self.content_dict = {}

    def preprocess(self,text):
        text = re.sub(r'\n{3,}', '\n', text)
        text = re.sub(r'\\{2,}', r'\\', text)

        arr = text.split('\n')
        for i in range(len(arr)):
            line = arr[i]
            if re.match(r'\\{1,}-+', line):
                line = re.sub(r'\\', '', line)
                arr[i] = line

        text = '\n'.join(arr)
        return text

    def readFromFile(self):
        if self.encryptionModule:
            # Encrypted notebook
            with open(self.file_path, "r") as reader:
                self.safe_copy = reader.read()
                decrypted_string = self.encryptionModule.decrypt(self.safe_copy.encode())
                self.content_dict = json.loads(decrypted_string)
        else:
            # Regular notebook
            with open(self.file_path, "r") as reader:
                self.content_dict = json.load(reader)

    def writeToFile(self):
        if self.encryptionModule:
            # Encrypted notebook
            try:
                with open(self.file_path, "w") as writer:
                    raw_content = json.dumps(self.content_dict)
                    encrypted_text = self.encryptionModule.encrypt(raw_content.encode()).decode()
                    writer.write(encrypted_text)
                    self.safe_copy = encrypted_text
            except:
                writer.write(self.safe_copy)
        else:
            # Regular notebook
            with open(self.file_path, "w") as writer:
                json.dump(self.content_dict, writer, indent=4)
                
    def upsert_without_write(self, key, val):
        if val == '':
            try:
                del self.content_dict[key]
            except:
                pass
        else:
            self.content_dict[key] = val

    def search(self, query):
        query = query.lower()
        if query == '':
            return self.content_dict
        result_set = {}
        for entryDate in self.content_dict.keys():
            if query in self.content_dict[entryDate].lower():
                result_set[entryDate] = self.content_dict[entryDate]

        return result_set