# database/connection.py
from matplotlib.backend_bases import cursors
import mysql.connector
from config.config import GLOBAL_CONFIG
from utils.logger import get_class_logger

logger = get_class_logger(__name__, "DBConnectionManager")

class DBConnectionManager:
    """
    Context Manager for MySQL database connections. 
    Guarantees that the connection and cursor are closed and transactions are committed.
    """
    def __init__(self, commit_on_success: bool = True,
                 table: str = None):
        self._conn = None
        self.cursor = None
        self._commit_on_success = commit_on_success
        self.config = GLOBAL_CONFIG
        self.logger = logger
        self.database = self.config.DB_NAME
        self.logger.info(f"Initialize Connection manager with cursor: {self.cursor}")

    def __enter__(self):
        """Opens the connection and creates a cursor."""
        try:
            # 1. Establish the connection using config values
            self._conn = mysql.connector.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                # Set database name if you have one configured
                database=self.database, 
                connection_timeout=self.config.DEFAULT_TIMEOUT_SEC
            )
            # 2. Create the cursor
            self.cursor = self._conn.cursor(dictionary=True) # dictionary=True returns rows as dicts
            logger.debug("Database connection established and cursor opened.")
            return self

        except mysql.connector.Error as e:
            logger.critical(f"Failed to connect to MySQL database: {e}", exc_info=True)
            # Raise the exception to prevent the 'with' block from executing
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the cursor and connection, handling commit/rollback."""
        try:
            if self.cursor:
                self.cursor.close()
                logger.debug("Database cursor closed.")

            if self._conn:
                if exc_type is None and self._commit_on_success:
                    # No exception occurred, commit changes if enabled
                    self._conn.commit()
                    logger.debug("Transaction committed successfully.")
                else:
                    # Exception occurred or commit disabled, rollback
                    self._conn.rollback()
                    if exc_type:
                        logger.warning(f"Transaction rolled back due to exception: {exc_val}")
                    else:
                        logger.debug("Transaction rolled back (commit disabled).")
                
                self._conn.close()
                logger.debug("Database connection closed.")
        
        except Exception as e:
            logger.error(f"Error during database cleanup: {e}")
        
        # Returning False (or letting the function finish without return) re-raises 
        # any exception caught in the 'with' block, which is standard context manager behavior.
        return False
    
    def fetch_one(self,
                  query: str,
                  params: tuple = None) -> dict:
        self.cursor.execute(query, params)
        return self.cursor.fetchone()
    
    def fetch_all (self,
                   query: str,
                   params: tuple) -> list[dict]:
        self.cursor.execute(query, params)
        return self.cursor.fetchall()