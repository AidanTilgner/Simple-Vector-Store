import sqlite3
import os
from utils.store import Store
from typing import Tuple

class Datastore:
    def __init__(self, location: str) -> None:
        if not os.path.exists(location):
            os.makedirs(location)

        self.location = location
        self.db_path = os.path.join(self.location, "datastore.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.conn.close()

    def reset_db(self):
        self.cursor.execute("DROP TABLE IF EXISTS stores")
        self.create_stores_table()

    def create_stores_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stores (
                id integer PRIMARY KEY,
                location text NOT NULL,
                name text NOT NULL UNIQUE
            )
            """
        )

    def add_new_store(self, name: str, location: str) -> None:
        self.cursor.execute(
            """
            INSERT INTO stores (name, location)
            VALUES (?, ?)
            """,
            (name, location),
        )
        self.conn.commit()
        
        os.makedirs(os.path.join(self.location, name))
        Store(os.path.join(self.location, name))

    def get_db_store(self, name: str) -> Tuple[str, str]:
        self.cursor.execute(
            """
            SELECT name, location FROM stores WHERE name = ?
            """,
            (name,),
        )
        return self.cursor.fetchone()

    def get_all_db_stores(self) -> list[Tuple[str, str]]:
        self.cursor.execute(
            """
            SELECT name, location FROM stores
            """
        )
        return self.cursor.fetchall()

    def remove_store(self, name: str) -> None:
        self.cursor.execute(
            """
            DELETE FROM stores WHERE name = ?
            """,
            (name,),
        )
        self.conn.commit()

        os.rmdir(os.path.join(self.location, name))

    def rename_store(self, old_name: str, new_name: str) -> None:
        self.cursor.execute(
            """
            UPDATE stores SET name = ? WHERE name = ?
            """,
            (new_name, old_name),
        )
        self.conn.commit()

        os.rename(
            os.path.join(self.location, old_name),
            os.path.join(self.location, new_name),
        )
