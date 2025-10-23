# config/config_manager.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Step 1: Define the path to the .env file relative to this script
# os.path.dirname(__file__) gets the directory of config_manager.py
CURRENT_FILE_PATH = Path(__file__).resolve()

# 2. Find the project root by navigating up twice:
#    .parent (gets 'config' folder) -> .parent (gets 'ML_PyQt_Project' root)
PROJECT_ROOT = CURRENT_FILE_PATH.parent.parent

# 3. Construct the absolute path to the .env file
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)

class ConfigManager:
    """
    A Singleton-like class to manage all application configurations.
    
    Configuration values are extracted directly from environment variables 
    (loaded from .env) and are accessed via class attributes (e.g., GLOBAL_CONFIG.DB_HOST).
    """
    def __init__(self):
        # ---------------------
        # Database Settings
        # ---------------------
        # os.getenv retrieves the variable, with a default if not found (good practice)
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = os.getenv("DB_PORT", "5432")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_NAME =os.getenv("DB_NAME")
        
        # ---------------------
        # ML and Application Settings
        # ---------------------
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        self.MODEL_PATH = os.getenv("MODEL_PATH", "assets/model.pkl")
        self.DEFAULT_TIMEOUT_SEC = int(os.getenv("DEFAULT_TIMEOUT_SEC", 60))
        
        # ---------------------
        # Logger
        # ---------------------
        self.LOGGER_CLASS_COLOR = os.getenv("LOGGER_CLASS_COLOR")
        

    def get_db_uri(self):
        """Helper to construct a standard database URI."""
        # Note: You should specify the dialect (e.g., 'postgresql', 'mysql') here.
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/app_db"

    # You can add other utility methods here, like 'get_api_key()' or 'get_asset_path()'
    
# Step 4: Instantiate the manager once and export it for global use.
# This ensures that all modules import and use the *exact same* configuration object.
GLOBAL_CONFIG = ConfigManager()