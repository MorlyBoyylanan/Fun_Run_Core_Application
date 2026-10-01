import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt, QDate
from database.database import Database
from .repository import ParticipantRepository
from .service import ParticipantService
from .model import Participant

class RegistrationPage(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setAttribute(
            Qt.WA_StyledBackground,
            True
        )

        # Load the UI
        uic.loadUi("features/registrationFrontPage/registrationBg.ui",self)

        # Get the background image path
        background_image_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "background", "FirstBackground.png")

        background_image_path = os.path.abspath(background_image_path)

        background_image_path = background_image_path.replace( "\\", "/")

        # Give the main widget an object name
        self.setObjectName(
            "MainRegistrationPage"
        )

        self.setStyleSheet(f"""
        QWidget#MainRegistrationPage {{
            border-image: url("{background_image_path}")
            1 0 0 0 stretch stretch;
        }}
        """)

        # Connect the buttons
        self.searchButton.clicked.connect(self.searchBtn)
        self.cancelButton.clicked.connect(self.cancelBtn)
        self.registerButton.clicked.connect(self.addBtn)
        self.updateButton.clicked.connect(self.updateBtn)
        self.deleteButton.clicked.connect(self.deleteBtn)
        self.clearButton.clicked.connect(self.clearBtn)
        self.tableWidget.itemSelectionChanged.connect(self.loadSelectedRow)
        
        # Set the table headers
        self.headers = (
            "Name",
            "Age",
            "Sex",
            "Birthdate",
            "Email",
            "CP Number",
            "Address",
            "Category",
            "Distance",
            "Race Number"
        )

        self.tableWidget.setColumnCount(len(self.headers))
        self.tableWidget.setHorizontalHeaderLabels(self.headers)

        # Create the database
        self.database = Database("FunRun.db")
        self.database.create_table()

        # Create the repository
        self.repository = ParticipantRepository(self.database)

        # Create the service
        self.service = ParticipantService(self.repository)

        # Load participants from the database
        self.loadFile()

    def addBtn(self):
        try:
            # Get values from input fields
            name = self.fullnametxt.text().strip()
            age = self.agetxt.text().strip()
            sex = self.sexcomboBox.currentText()
            birthdate = self.birthdateEdit.date().toString("yyyy-MM-dd")
            email = self.emailtxt.text().strip()
            cpnumber = self.cptxt.text().strip()
            address = self.addresstxt.text().strip()
            category = self.categorycomboBox.currentText()
            distance = self.distancecomboBox.currentText()
            race_number = self.racenumbertxt.text().strip()

            # Send data to the service

            participant = self.service.register_participant(
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

            # Display participant in table
            self.displayParticipant(participant)
            QMessageBox.information(self, "Registration Successful", "Participant registered successfully.")

            # Clear input fields
            self.clearBtn()

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Input Error",
                str(error)
            )

        except Exception as error:
            QMessageBox.critical(self,"Error", f"An error occurred:\n{error}")

    # Function to display a participant in the table
    def displayParticipant(self, participant):
        row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row)

        values = (
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

        for column, value in enumerate(values):

            self.tableWidget.setItem(
                row,
                column,
                QTableWidgetItem(value)
            )

    # Function to load participants from the database
    def loadFile(self):
        try:
            participants = self.repository.get_all()

            for row in participants:
                participant = Participant(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                    row[9]
                )

                self.displayParticipant(participant)

        except Exception as error:
            QMessageBox.critical(self, "Database Error", f"Unable to load participants:\n{error}")

    # Function to load the selected row's data
    def loadSelectedRow(self):
        selected_row = self.tableWidget.currentRow()

        if selected_row < 0:
            return

        try:
            self.fullnametxt.setText(self.tableWidget.item(selected_row, 0).text())
            self.agetxt.setText(self.tableWidget.item(selected_row, 1).text())
            self.sexcomboBox.setCurrentText(self.tableWidget.item(selected_row, 2).text())

            birthdate = self.tableWidget.item(selected_row, 3).text()
            date = QDate.fromString(
                birthdate,
                "yyyy-MM-dd"
            )
            self.birthdateEdit.setDate(date)
            self.emailtxt.setText(self.tableWidget.item(selected_row, 4).text())
            self.cptxt.setText(self.tableWidget.item(selected_row, 5).text())
            self.addresstxt.setText(self.tableWidget.item(selected_row, 6).text())
            self.categorycomboBox.setCurrentText(self.tableWidget.item(selected_row, 7).text())
            self.distancecomboBox.setCurrentText(self.tableWidget.item(selected_row, 8).text())
            self.racenumbertxt.setText(self.tableWidget.item(selected_row, 9).text())

        except Exception as error:
            QMessageBox.warning(self,"Selection Error",f"Unable to load selected participant:\n{error}")

    # Function to update the selected participant
    def updateBtn(self):
        selected_row = self.tableWidget.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self,"Input Error","Please select a participant to update.")
            return

        try:
            old_race_number = self.tableWidget.item(
                selected_row,
                9
            ).text()

            name = self.fullnametxt.text().strip()
            age = self.agetxt.text().strip()
            sex = self.sexcomboBox.currentText()
            birthdate = self.birthdateEdit.date().toString(
                "yyyy-MM-dd"
            )
            email = self.emailtxt.text().strip()
            cpnumber = self.cptxt.text().strip()
            address = self.addresstxt.text().strip()
            category = self.categorycomboBox.currentText()
            distance = self.distancecomboBox.currentText()
            race_number = self.racenumbertxt.text().strip()

            # Send updated data to the service

            participant = self.service.update_participant(
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
            )

            # Update the table

            values = (
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

            for column, value in enumerate(values):

                self.tableWidget.setItem(
                    selected_row,
                    column,
                    QTableWidgetItem(value)
                )

            QMessageBox.information(
                self,
                "Update Successful",
                "Participant updated successfully."
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Input Error",
                str(error)
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Update Error",
                f"Unable to update participant:\n{error}"
            )

    # Function to delete a participant
    def deleteBtn(self):

        selected_row = self.tableWidget.currentRow()

        if selected_row < 0:

            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a participant to delete."
            )

            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this participant?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:

            try:

                race_number = self.tableWidget.item(
                    selected_row,
                    9).text()

                self.service.delete_participant(race_number)

                self.tableWidget.removeRow(selected_row)

                QMessageBox.information(self, "Delete Successful", "Participant deleted successfully.")

            except Exception as error:

                QMessageBox.critical(self, "Delete Error", f"Unable to delete participant:\n{error}")

    # Function to search for a participant
    def searchBtn(self):

        search_txt = self.searchtxt.text().strip().lower()

        if not search_txt:

            QMessageBox.warning(
                self,
                "Input Error",
                "Please enter a race number or name to search.")
            return

        found = False

        for row in range(self.tableWidget.rowCount()):
            name_item = self.tableWidget.item(row, 0)
            race_number_item = self.tableWidget.item(row, 9)

            name = name_item.text().lower() if name_item else ""
            race_number = race_number_item.text().lower() if race_number_item else ""

            if search_txt in name or search_txt == race_number:

                self.tableWidget.selectRow(row)
                found = True
                QMessageBox.information(
                    self,
                    "Search Result",
                    f"Participant found: {name_item.text()} (Race Number: {race_number_item.text()})")
                break

        if not found:
            QMessageBox.information(
                self,
                "Search Result",
                "Participant not found.")
    # Function to clear all input fields
    def clearBtn(self):

        self.fullnametxt.clear()
        self.agetxt.clear()
        self.sexcomboBox.setCurrentIndex(0)
        self.birthdateEdit.setDate(
            QDate.currentDate()
        )
        self.emailtxt.clear()
        self.cptxt.clear()
        self.addresstxt.clear()
        self.categorycomboBox.setCurrentIndex(0)
        self.distancecomboBox.setCurrentIndex(0)
        self.racenumbertxt.clear()

    # Function to cancel the registration

    def cancelBtn(self):
        self.clearBtn()