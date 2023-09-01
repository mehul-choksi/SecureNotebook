import json

from cryptography.fernet import Fernet

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import base64
import re

class FileStorage():

    def __init__(self):
        # Todo: Finalize path and where it is stored
        self.file_path = './data'
        self.content_dict = {}
        self.safe_copy = ''
        self.passphrase = None

    def initialize(self, passphrase):
        self.passphrase = passphrase
        key = self.generate_fernet_key_from_password(self.passphrase)
        self.encryptionModule = Fernet(key)

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

    def readFromFile(self):
        if self.passphrase is not None:
            reader = open(self.file_path)
            self.safe_copy = reader.read()
            decrypted_string = self.encryptionModule.decrypt(self.safe_copy.encode())
            self.content_dict = json.loads(decrypted_string)
            # print('Decrypted content ', self.content_dict)
        else:
            raise ValueError('Passphrase has not been initialized')

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

    def writeToFile(self):
        if self.passphrase is not None:
            try: 
                writer = open(self.file_path, 'w')
                # Convert all html into markdown stuff prior to storing
                # This allows markdown library to convert this format back to html, next time write is made
                for currentDate in self.content_dict.keys():
                    self.content_dict[currentDate] = self.preprocess(self.content_dict[currentDate])
                raw_content = json.dumps(self.content_dict)
                # Encrypt the text. encode() and decode() are functions to convert to bytecode and text.
                encrypted_text = self.encryptionModule.encrypt(raw_content.encode()).decode()
                writer.write(encrypted_text)
                self.safe_copy = encrypted_text
            except:
                print("Error in writing contents...., rolling back to last valid state")
                writer.write(self.safe_copy)
        else:
            raise ValueError('Passphrase has not been initialized')

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