import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    
    # Database
    BASE_DIR = os.path.dirname(__file__)
    DATABASE_PATH = os.path.join(BASE_DIR, 'database')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(DATABASE_PATH, "shares.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Default expiration times (in seconds)
    DEFAULT_EXPIRY_OPTIONS = {
        '5_minutes': 300,
        '30_minutes': 1800,
        '1_hour': 3600,
        '6_hours': 21600,
        '12_hours': 43200,
        '24_hours': 86400,
        '7_days': 604800
    }
    
    # Cleanup interval (in seconds)
    CLEANUP_INTERVAL = 3600  # Run cleanup every hour

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}