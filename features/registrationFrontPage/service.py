from .model import Participant


class ParticipantService:

    def __init__(self, repository):
        self.repository = repository

    # Function to register a participant

    def register_participant(self, name, age, sex, birthdate, email,
                             cpnumber, address, category, distance, race_number):
        # Validate input fields
        if not name or not age or not email \
                or not cpnumber or not address \
                or not race_number:

            raise ValueError(
                "Please fill in all the fields."
            )

        # Check duplicate race number

        if self.repository.race_number_exists(
            race_number
        ):

            raise ValueError(
                "Race number already exists. "
                "Please enter a unique race number."
            )

        # Create participant

        participant = Participant(name, age, sex, birthdate, email, cpnumber, 
                                  address, category, distance, race_number)

        # Save participant to database
        self.repository.add(participant)

        return participant

    # Function to update a participant
    def update_participant(
        self,
        old_race_number,
        name,
        age,
        sex,
        birthdate,
        email,
        cpnumber,
        address,
        category,
        distance,
        race_number
    ):

        # Validate input fields

        if not name or not age or not email \
                or not cpnumber or not address \
                or not race_number:

            raise ValueError(
                "Please fill in all the fields."
            )

        # Check duplicate race number

        if race_number != old_race_number:

            if self.repository.race_number_exists(
                race_number
            ):

                raise ValueError(
                    "Race number already exists."
                )

        # Create updated participant

        participant = Participant(
            name,
            age,
            sex,
            birthdate,
            email,
            cpnumber,
            address,
            category,
            distance,
            race_number
        )

        # Update participant in database

        self.repository.update(
            old_race_number,
            participant
        )

        return participant

    # Function to delete a participant

    def delete_participant(self, race_number):

        self.repository.delete(race_number)