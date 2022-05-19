import sqlite3
from typing import Literal
from pathlib import Path

DB_PATH = ':memory:'

class Store:
    def __init__(self, db: Path | str = DB_PATH):
        db = str(db.resolve()) if isinstance(db, Path) else db
        self.connection = sqlite3.connect(db)

    def __enter__(self):
        return self.connection.__enter__()

    def __exit__(self):
        return self.connection.__exit__()
