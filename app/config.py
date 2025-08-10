"""
Configuration management for AutoBlog-Pipe
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Git Configuration
    GIT_USER_NAME = os.getenv('GIT_USER_NAME', 'AutoBot')
    GIT_USER_EMAIL = os.getenv('GIT_USER_EMAIL', 'bot@example.com')
    GIT_REPO_SSH = os.getenv('GIT_REPO_SSH')
    
    # Site Configuration
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Seoul')
    POSTS_PER_RUN = int(os.getenv('POSTS_PER_RUN', 1))
    SITE_BASE_URL = os.getenv('SITE_BASE_URL')
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    BASE_DIR = PROJECT_ROOT  # 호환성을 위해 유지
    APP_DIR = PROJECT_ROOT / 'app'
    SITE_DIR = PROJECT_ROOT / 'site'
    TOPICS_FILE = APP_DIR / 'topics' / 'topics.yml'
    PROMPTS_DIR = APP_DIR / 'prompts'
    POSTS_DIR = SITE_DIR / '_posts'
    
    # Git Configuration (추가)
    GIT_COMMIT_TEMPLATE = os.getenv('GIT_COMMIT_TEMPLATE', 'feat: 새 블로그 글 발행 - {title}')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        missing = []
        if not cls.OPENAI_API_KEY:
            missing.append('OPENAI_API_KEY')
        if not cls.GIT_REPO_SSH:
            missing.append('GIT_REPO_SSH')
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True