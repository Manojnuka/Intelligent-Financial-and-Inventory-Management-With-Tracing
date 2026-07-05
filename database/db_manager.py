"""SQLite database utilities - Functional implementation."""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, TypeVar
from contextlib import contextmanager
import pandas as pd

from config.settings import get_settings


# Type variables for generic functions
T = TypeVar('T')


def dict_factory(cursor, row):
    """Convert SQLite row to dictionary."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@contextmanager
def get_connection():
    """Get SQLite connection with automatic commit/rollback.
    """
    settings = get_settings()
    conn = sqlite3.connect(settings.db_path_resolved)
    conn.row_factory = dict_factory
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def query(sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """Run SELECT query and return results as list of dicts.

    Args:
        sql: SQL query string
        params: Query parameters

    Returns:
        List of dictionaries containing query results
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        return cursor.fetchall()


def execute(sql: str, params: Optional[tuple] = None) -> int:
    """Run INSERT/UPDATE/DELETE query and return affected row count.

    Args:
        sql: SQL statement
        params: Statement parameters

    Returns:
        Number of affected rows
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        return cursor.rowcount


def to_dataframe(sql: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """Execute query and return results as pandas DataFrame.

    Args:
        sql: SQL query string
        params: Query parameters

    Returns:
        DataFrame containing query results
    """
    with get_connection() as conn:
        conn.row_factory = None
        return pd.read_sql_query(sql, conn, params=params)


def execute_script(script_path: Path) -> None:
    """Execute SQL script file.

    Args:
        script_path: Path to SQL script file
    """
    with open(script_path, 'r') as f:
        script_content = f.read()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executescript(script_content)


def with_transaction(func: Callable[[Any], T]) -> T:
    """Execute a function within a database transaction.

    Higher-order function that provides transactional safety for complex operations.

    Args:
        func: Function that takes a connection and returns a value

    Returns:
        Result of the function
    """
    with get_connection() as conn:
        return func(conn)
