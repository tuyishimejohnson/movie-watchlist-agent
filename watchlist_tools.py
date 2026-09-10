import random
import sqlite3
from pathlib import Path

from langchain.tools import tool

DB_PATH = Path(__file__).parent / "watchlist.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE
        )
        """)
    return conn


# Add movies
@tool
def add_movies(title: str) -> str:
    """Add a movie to the watchlist."""
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT title FROM movies WHERE lower(title) = lower(?)", (title,)
        ).fetchone()
        if existing:
            return f"{existing[0]} already exists"
        conn.execute("INSERT INTO movies (title) VALUES (?)", (title,))
        return f"{title} added to your list"


# remove a movie
@tool
def remove_movies(title: str) -> str:
    """Remove a movie from the watchlist."""
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT title FROM movies WHERE lower(title) = lower(?)", (title,)
        ).fetchone()
        if not existing:
            return f"{title} does not exist in your list"
        conn.execute("DELETE FROM movies WHERE lower(title) = lower(?)", (title,))
        return f"{existing[0]} removed from your list"


# randomly select a movie
@tool
def random_movie() -> str:
    """Suggest a random movie from the watchlist."""
    with get_connection() as conn:
        titles = [row[0] for row in conn.execute("SELECT title FROM movies")]
    if not titles:
        return "Your movie list is empty"
    return f"Random movie suggestion: {random.choice(titles)}"


# list all movies
@tool
def list_movies() -> str:
    """List all movies in the watchlist."""
    with get_connection() as conn:
        titles = [
            row[0] for row in conn.execute("SELECT title FROM movies ORDER BY id")
        ]
    if not titles:
        return "Your movie list is empty"
    return "Your movie list:\n" + "\n".join(titles)
