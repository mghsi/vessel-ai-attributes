import os
from pathlib import Path


class Config:
    """Base configuration class"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER") or os.path.join(
        Path(__file__).parent.parent, "uploads"
    )
    MAX_CONTENT_LENGTH = int(
        os.environ.get("MAX_CONTENT_LENGTH") or 16 * 1024 * 1024
    )  # 16MB max file size
    ALLOWED_EXTENSIONS = set(
        os.environ.get("ALLOWED_EXTENSIONS", "png,jpg,jpeg,gif,bmp,webp").split(",")
    )

    # GitHub Models API settings
    GITHUB_PAT = os.environ.get("GITHUB_PAT")
    GITHUB_API_URL = (
        os.environ.get("GITHUB_API_URL")
        or "https://models.inference.ai.azure.com/chat/completions"
    )
    DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL") or "gpt-4o"


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
