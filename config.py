# config.py slave

import os
import pymysql
import logging

class Config:
    """Configuration settings for the application."""
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '123'),
        'db': os.getenv('DB_NAME', 'IoTLocal'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

class Logger:
    """Logger configuration."""
    @staticmethod
    def configure():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
