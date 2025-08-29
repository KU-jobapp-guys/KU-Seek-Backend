"""Module containing the base class for all controllers."""


import sys
import pymysql
from dbutils.pooled_db import PooledDB
from decouple import config


OPENAPI_STUB_DIR = config("OPENAPI_STUB_DIR", default="swagger_server")

sys.path.append(OPENAPI_STUB_DIR)


class BaseController():
    """Base class for creating controllers."""

    def __init__(self):
        """Initialize the class."""
        self.pool = self.__get_database()

    def __get_database(self):
        """Get a database instace."""
        pool = PooledDB(
            creator=pymysql,
            host=config("DB_HOST", default="127.0.0.1"),
            port=config("DB_PORT", cast=int, default="1234"),
            user=config("DB_USER", default="root"),
            password=config("DB_PASSWORD", default="mysecrtpw123"),
            database=config("DB_NAME", default="defaultdb"),
            maxconnections=1,
            connect_timeout=10,
            blocking=True,
        )
        try:
            with pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS tasks (
                            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            completed BOOLEAN DEFAULT FALSE
                        );
                    """)
                    conn.commit()
            print("Database initialized")
            return pool
        except Exception as e:
            print(f"Error initializing database pool: {e}")

    def execute_query(
        self,
        query: str,
        params: tuple = None,
        fetchone: bool = False,
        fetchall: bool = False,
        commit=False,
    ):
        """
        Convienience method for executing queries.

        Executes a given SQL query using a connection from the pool.
        Handles connection management, commits, rollbacks, and error logging.

        Args:
            query: The SQL query string to execute.
            params: A tuple of parameters to pass to the query. Defaults to None.
            fetchone: If True, fetches a single row. Defaults to False.
            fetchall: If True, fetches all rows. Defaults to False.
            commit: If true, commits the query to modify the table.

        Returns: Fetched data (dict for one, list of dicts for all)
                or None for DML operations.
        Raises:
            Exception: Re-raises any database-related exceptions after logging.
        """
        conn = None
        cursor = None
        try:
            conn = self.pool.connection()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query, params)
            if commit:
                conn.commit()

            if fetchone:
                return cursor.fetchone()
            elif fetchall:
                return cursor.fetchall()
            return {"message": "Query executed"}
        except Exception as e:
            print(f"Database error during query execution: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()   
