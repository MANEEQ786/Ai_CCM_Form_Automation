import os, sys
import pymssql
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import logging
info_logger = logging.getLogger('api_info')
error_logger = logging.getLogger('api_error')

load_dotenv(override=True)

def get_password(encrypted_password: bytes,key) -> str:
    try:
        fernet = Fernet(key)
        decrypted_password = fernet.decrypt(encrypted_password).decode()
        return decrypted_password
    except Exception as e:
        raise e


Wellness_DB_HOST = os.getenv("WELLNESS_DB_HOST")
Wellness_DB_USER = os.getenv("WELLNESS_DB_USER")
Wellness_DB_NAME = os.getenv("WELLNESS_DB_NAME")
Wellness_DB_PASSWORD = os.getenv("WELLNESS_DB_PWD")
WKEY = os.getenv("WKEY")
Wellness_DB_PASSWORD = get_password(Wellness_DB_PASSWORD,WKEY)


Talk_DB_HOST = os.getenv("LIVE_DB_HOST")
Talk_DB_USER = os.getenv("LIVE_DB_USER")
Talk_DB_NAME = os.getenv("LIVE_DB_NAME")
Talk_DB_PASSWORD = os.getenv("LIVE_DB_PWD")
TKEY = os.getenv("TKEY")
Talk_DB_PASSWORD = get_password(Talk_DB_PASSWORD,TKEY)


class DatabaseConnectionManager:

    def __init__(self, env="Wellness"):
        if env == "Wellness":
            self.server = Wellness_DB_HOST
            self.user = Wellness_DB_USER
            self.password = Wellness_DB_PASSWORD
            self.database = Wellness_DB_NAME 
        elif env == "Talk":
            self.server = Talk_DB_HOST
            self.user = Talk_DB_USER
            self.password = Talk_DB_PASSWORD
            self.database = Talk_DB_NAME 

        else:
            error_logger.error("error")
            raise ValueError("Invalid environment specified. Use 'Wellness' or 'Talk'.")
        
    def __enter__(self):
        try:
            self.conn = pymssql.connect(
                server=self.server,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return self.conn
        except pymssql.DatabaseError as e:
            error_logger.error(str(e))
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
