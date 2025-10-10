import os

class Config:
    DB_HOST = os.getenv("DB_HOST", "185.232.14.52")
    DB_NAME = os.getenv("DB_NAME", "u760464709_23005210_bd")
    DB_USER = os.getenv("DB_USER", "u760464709_23005210_usr")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "~3qAQp|V0aD")
    PUSHER_APP_ID = os.getenv("PUSHER_APP_ID", "2046048")
    PUSHER_KEY = os.getenv("PUSHER_KEY", "bc1c723155afce8dd187")
    PUSHER_SECRET = os.getenv("PUSHER_SECRET", "57fd29b7d864a84bf88c")
    PUSHER_CLUSTER = os.getenv("PUSHER_CLUSTER", "us2")
