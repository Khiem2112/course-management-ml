# database/crud.py
from connection_manager import DBConnectionManager
from utils.logger import get_class_logger

logger = get_class_logger(__name__, "DBExecuteService")

class DBExecuteService:
    """
    A service class that executes custom SQL queries, handling
    connection management, transaction commitment, and data retrieval.
    """

    @staticmethod
    def fetch_one(query: str, params: tuple = None) -> dict | None:
        """Executes a query and returns a single row as a dictionary."""
        try:
            # READ operation - commit_on_success=False
            with DBConnectionManager(commit_on_success=False) as db:
                result = db.fetch_one(query, params)
                logger.debug(f"Executed fetch_one query. Result found: {result is not None}")
                return result
        except Exception as e:
            logger.error(f"Failed to fetch single record with query: {query}", exc_info=True)
            return None

    @staticmethod
    def fetch_all(query: str, params: tuple = None) -> list[dict]:
        """Executes a query and returns all rows as a list of dictionaries."""
        try:
            # READ operation - commit_on_success=False
            with DBConnectionManager(commit_on_success=False) as db:
                results = db.fetch_all(query, params)
                logger.debug(f"Executed fetch_all query. Rows returned: {len(results)}")
                return results
        except Exception as e:
            logger.error(f"Failed to fetch all records with query: {query}", exc_info=True)
            return []

    @staticmethod
    def execute_query(query: str, params: tuple = None, return_id: bool = False) -> int | bool:
        """
        Executes a non-READ query (INSERT, UPDATE, DELETE, DDL).
        Commits changes upon success.
        
        Args:
            query (str): The custom SQL query string.
            params (tuple): Parameters to bind to the query.
            return_id (bool): If True, attempts to return the last inserted ID.
            
        Returns:
            The last inserted ID (if return_id is True), or a boolean (success/fail).
        """
        try:
            # WRITE/EXECUTE operation - commit_on_success=True (default)
            with DBConnectionManager() as db:
                db.cursor.execute(query, params)
                
                if return_id:
                    new_id = db.cursor.lastrowid
                    logger.info(f"Executed query (INSERT). New ID: {new_id}")
                    return new_id
                
                row_count = db.cursor.rowcount
                logger.info(f"Executed query (UPDATE/DELETE). Rows affected: {row_count}")
                return True # Success
                
        except Exception as e:
            logger.error(f"Failed to execute query: {query}. Transaction rolled back.", exc_info=True)
            return False