
class ParticipantRepository:

    def __init__(self, database):
        self.database = database

    # Generate the next available race number
    def generate_race_number(self):
        with self.database.connect() as connection:
            cursor = connection.execute(
                "SELECT race_number FROM participants"
            )
            race_numbers = cursor.fetchall()

        highest_number = 0

        for row in race_numbers:
            try:
                number = int(row[0])
                highest_number = max(highest_number, number)
            except (ValueError, TypeError):
                continue

        next_number = highest_number + 1
        return f"{next_number:04d}"

    # Function to add a participant to the database
    def add(self, participant):

        with self.database.connect() as connection:

            connection.execute(
                """
                INSERT INTO participants (
                    name, age, sex, birthdate, email,
                    cpnumber, address, category, distance,
                    race_number
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    participant.name,
                    participant.age,
                    participant.sex,
                    participant.birthdate,
                    participant.email,
                    participant.cpnumber,
                    participant.address,
                    participant.category,
                    participant.distance,
                    participant.race_number
                )
            )

    # Function to get all participants from the database
    def get_all(self):

        with self.database.connect() as connection:

            cursor = connection.execute(
                """
                SELECT name, age, sex, birthdate, email,
                       cpnumber, address, category, distance,
                       race_number
                FROM participants
                """
            )

            return cursor.fetchall()

    # Function to check if a race number already exists
    def race_number_exists(self, race_number):

        with self.database.connect() as connection:

            cursor = connection.execute(
                """
                SELECT 1
                FROM participants
                WHERE race_number = ?
                """,
                (race_number,)
            )

            return cursor.fetchone() is not None

    # Function to update a participant
    def update(self, old_race_number, participant):

        with self.database.connect() as connection:

            connection.execute(
                """
                UPDATE participants
                SET name = ?, age = ?, sex = ?, birthdate = ?,
                    email = ?, cpnumber = ?, address = ?,
                    category = ?, distance = ?, race_number = ?
                WHERE race_number = ?
                """,
                (
                    participant.name,
                    participant.age,
                    participant.sex,
                    participant.birthdate,
                    participant.email,
                    participant.cpnumber,
                    participant.address,
                    participant.category,
                    participant.distance,
                    participant.race_number,
                    old_race_number
                )
            )

    # Function to delete a participant
    def delete(self, race_number):

        with self.database.connect() as connection:

            connection.execute(
                """
                DELETE FROM participants
                WHERE race_number = ?
                """,
                (race_number,)
            )
