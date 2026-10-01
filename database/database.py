import sqlite3
from pathlib import Path


class Database:

    def __init__(self, database_path="FunRun.db"):
        self.database_path = Path(database_path)

    # Function to connect to the database

    def connect(self):
        return sqlite3.connect(self.database_path)

    # Function to create the participants table

    def create_table(self):

        with self.connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age TEXT NOT NULL,
                    sex TEXT NOT NULL,
                    birthdate TEXT NOT NULL,
                    email TEXT NOT NULL,
                    cpnumber TEXT NOT NULL,
                    address TEXT NOT NULL,
                    category TEXT NOT NULL,
                    distance TEXT NOT NULL,
                    race_number TEXT NOT NULL UNIQUE
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS race_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_number TEXT NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    distance TEXT NOT NULL,
                    race_time TEXT NOT NULL
                    
                )
                """
            )

    def get_participant_by_race_number(self, race_number):
        with self.connect() as connection:
            cursor = connection.execute(
                """
                SELECT name, category, distance
                FROM participants
                WHERE race_number = ?
                """,
                (race_number,)
            )

            return cursor.fetchone()
        
    def save_race_result(self, race_number, name, category, distance, race_time):
        with self.connect() as connection:

            existing = connection.execute(
                """
                SELECT id
                FROM race_results
                WHERE race_number = ?
                """,
                (race_number,)
            ).fetchone()

            if existing:
                return False

            connection.execute(
                """
                INSERT INTO race_results
                (race_number, name, category, distance, race_time)
                VALUES (?, ?, ?, ?, ?)
                """,
                (race_number, name, category, distance, race_time)
            )

            return True