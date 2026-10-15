import sqlite3
from pathlib import Path


class Database:

    def __init__(self, database_path=None):
        # Get the project root directory
        project_root = Path(__file__).resolve().parent.parent

        # Store the database in the project root
        if database_path is None:
            self.database_path = project_root / "FunRun.db"
        else:
            self.database_path = Path(database_path)

        # Create tables if they do not exist
        self.create_table()

    def connect(self):
        # Connect to the database
        connection = sqlite3.connect(self.database_path)

        # Enable foreign key enforcement
        connection.execute("PRAGMA foreign_keys = ON")

        return connection

    def create_table(self):
        with self.connect() as connection:

            # PARTICIPANTS TABLE
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

            # RACE RESULTS TABLE
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS race_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_number TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    distance TEXT NOT NULL,
                    race_time TEXT NOT NULL,
                    FOREIGN KEY (race_number)
                        REFERENCES participants (race_number)
                )
                """
            )

            # SINGLET RECORDS TABLE
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS singlet_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    race_number TEXT UNIQUE,
                    name TEXT NOT NULL,
                    category TEXT,
                    distance TEXT,
                    cpnumber TEXT,
                    singlet_size TEXT NOT NULL,
                    singlet_status TEXT NOT NULL DEFAULT 'Reserved',
                    FOREIGN KEY (race_number)
                        REFERENCES participants (race_number)
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

    # race_results table methods

    def save_race_result(self, race_number, name, category, distance, race_time):
        with self.connect() as connection:

            # Check whether this race number already has a result
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
                INSERT INTO race_results (
                    race_number,
                    name,
                    category,
                    distance,
                    race_time
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    race_number,
                    name,
                    category,
                    distance,
                    race_time
                )
            )

            return True

    def delete_race_result(self, race_number):
        with self.connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM race_results
                WHERE race_number = ?
                """,
                (race_number,)
            )

            return cursor.rowcount > 0

    def update_race_result(
        self, race_number, name, category, distance, race_time
    ):
        with self.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE race_results
                SET
                    name = ?,
                    category = ?,
                    distance = ?,
                    race_time = ?
                WHERE race_number = ?
                """,
                (
                    name,
                    category,
                    distance,
                    race_time,
                    race_number
                )
            )

            return cursor.rowcount > 0

    # SINGLET RECORDS TABLE METHODS

    def get_singlet_record_by_race_number(self, race_number):
        with self.connect() as connection:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    race_number,
                    name,
                    category,
                    distance,
                    cpnumber,
                    singlet_size,
                    singlet_status
                FROM singlet_records
                WHERE race_number = ?
                """,
                (race_number,)
            )

            return cursor.fetchone()
