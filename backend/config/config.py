import os
from pathlib import Path


class Config:
    """Base configuration class"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    UPLOAD_FOLDER = os.path.join(Path(__file__).parent.parent, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}

    # GitHub Models API settings
    GITHUB_PAT = os.environ.get("GITHUB_PAT")
    GITHUB_API_URL = "https://models.github.ai/inference/chat/completions"
    DEFAULT_MODEL = "openai/gpt-4.1"


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
