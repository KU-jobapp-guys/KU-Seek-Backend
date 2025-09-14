"""Module containing the base class for all controllers."""

import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from decouple import config


OPENAPI_STUB_DIR = config("OPENAPI_STUB_DIR", default="swagger_server")

sys.path.append(OPENAPI_STUB_DIR)


class BaseController:
    """Base class for creating controllers."""

    def __init__(self):
        """Initialize the class."""
        self.pool = self.__get_database()

    def __get_database(self):
        """Get a database instance."""
        host = config("DB_HOST", default="127.0.0.1")
        port = config("DB_PORT", cast=int, default="1234")
        user = config("DB_USER", default="root")
        password = config("DB_PASSWORD", default="mysecrtpw123")
        database = config("DB_NAME", default="defaultdb")

        connection_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

        db_engine = create_engine(
            connection_url,
            pool_size=1,
            max_overflow=0,
            pool_timeout=10,
        )

        try:
            with db_engine.connect() as pool:
                pool.execute(text("SELECT * FROM User"))
                print("Database initialization sucessful.")
            return db_engine
        except Exception as e:
            raise ConnectionRefusedError("Could not connect to database,", e)

    def get_session(self):
        """Return a session object for ORM usage."""
        return Session(self.pool)

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
            conn = self.pool.connect()
            res = conn.execute(text(query), params)
            if commit:
                conn.commit()

            if fetchone:
                return dict(res.fetchone()._mapping)
            elif fetchall:
                return [dict(row._mapping) for row in res.fetchall()]
            return {"message": "Query executed"}
        except Exception as e:
            print(f"Database error during query execution: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
