import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox
from database.database import Database


class ParticipantsDataRecordPage(QMainWindow):

    def __init__(self):
        super().__init__()

        uic.loadUi("features/participantsDataRecordFrontPage/participantsDataRecordUi.ui", self)

        
        background_image_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "background", "ThirdBackground.png")
        
        background_image_path = os.path.abspath(background_image_path)  
        background_image_path = background_image_path.replace( "\\", "/")

        self.setObjectName(
            "participantDataRecordPagebg"
            )
        
        self.setStyleSheet(f"""
        QWidget#participantDataRecordPagebg {{
            border-image: url("{background_image_path}")
            0 0 0 0 stretch stretch;
        }}
        """)

        self.database = Database()

        self.updateButton.clicked.connect(self.updateRecord)
        self.deleteButton.clicked.connect(self.deleteRecord)
        self.clearButton.clicked.connect(self.clearFields)
        self.searchButton.clicked.connect(self.searchRecord)
        self.searchLineEdit.textChanged.connect(self.searchTextChanged)

        self.openMenTable.cellClicked.connect(self.selectRecord)
        self.openWomenTable.cellClicked.connect(self.selectRecord)
        self.seniorCitizenMenTable.cellClicked.connect(self.selectRecord)
        self.seniorCitizenWomenTable.cellClicked.connect(self.selectRecord)

        self.loadRaceResults()

    def loadRaceResults(self):

        self.openMenTable.setRowCount(0)
        self.openWomenTable.setRowCount(0)
        self.seniorCitizenMenTable.setRowCount(0)
        self.seniorCitizenWomenTable.setRowCount(0)

        with self.database.connect() as connection:

            results = connection.execute(
                """
                SELECT race_number, name, category, distance, race_time
                FROM race_results
                ORDER BY race_time ASC
                """
            ).fetchall()

        category_tables = {
            "Open Men": self.openMenTable,
            "Open Women": self.openWomenTable,
            "Senior Citizen Men": self.seniorCitizenMenTable,
            "Senior Citizen Women": self.seniorCitizenWomenTable
        }

        category_results = {
            "Open Men": [],
            "Open Women": [],
            "Senior Citizen Men": [],
            "Senior Citizen Women": []
        }

        for result in results:
            race_number, name, category, distance, race_time = result

            if category in category_results:
                category_results[category].append(result)

        for category, records in category_results.items():

            table = category_tables[category]

            for rank, record in enumerate(records, start=1):

                race_number, name, category, distance, race_time = record

                row = table.rowCount()
                table.insertRow(row)

                if rank == 1:
                    rank_text = "1st"
                elif rank == 2:
                    rank_text = "2nd"
                elif rank == 3:
                    rank_text = "3rd"
                else:
                    rank_text = f"{rank}th"

                table.setItem(row, 0, QTableWidgetItem(rank_text))
                table.setItem(row, 1, QTableWidgetItem(race_number))
                table.setItem(row, 2, QTableWidgetItem(name))
                table.setItem(row, 3, QTableWidgetItem(distance))
                table.setItem(row, 4, QTableWidgetItem(race_time))

    def selectRecord(self, row, column):
        table = self.sender()

        rank = table.item(row, 0).text()
        race_number = table.item(row, 1).text()
        full_name = table.item(row, 2).text()
        distance = table.item(row, 3).text()
        race_time = table.item(row, 4).text()

        self.rankLineEdit.setText(rank)
        self.raceNumberLineEdit.setText(race_number)
        self.fullNameLineEdit.setText(full_name)
        self.distanceComboBox.setCurrentText(distance)
        self.raceTimeLineEdit.setText(race_time)

        category_map = {
            "openMenTable": "Open Men",
            "openWomenTable": "Open Women",
            "seniorCitizenMenTable": "Senior Citizen Men",
            "seniorCitizenWomenTable": "Senior Citizen Women"
        }

        category = category_map.get(table.objectName())

        if category:
            self.categoryComboBox.setCurrentText(category)

    def updateRecord(self):
        race_number = self.raceNumberLineEdit.text().strip()
        name = self.fullNameLineEdit.text().strip()
        category = self.categoryComboBox.currentText()
        distance = self.distanceComboBox.currentText()
        race_time = self.raceTimeLineEdit.text().strip()

        if not race_number or not name or not category or not distance or not race_time:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please select a record and complete all fields."
            )
            return

        success = self.database.update_race_result(
            race_number,
            name,
            category,
            distance,
            race_time
        )

        if success:
            QMessageBox.information(self, "Updated", "Race result updated successfully.")

            self.loadRaceResults()

    def deleteRecord(self):
        race_number = self.raceNumberLineEdit.text().strip()

        if not race_number:
            QMessageBox.warning(
                self,
                "No Record Selected",
                "Please select a race result first."
            )
            return

        reply = QMessageBox.question(
            self,
            "Delete Record",
            f"Are you sure you want to delete Race Number {race_number}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        success = self.database.delete_race_result(race_number)

        if success:
            QMessageBox.information(
                self,
                "Deleted",
                "Race result deleted successfully."
            )

            self.clearFields()
            self.loadRaceResults()


    def searchRecord(self):
        search_text = self.searchLineEdit.text().strip()

        if not search_text:
            self.loadRaceResults()
            return

        with self.database.connect() as connection:

            results = connection.execute(
                """
                SELECT race_number, name, category, distance, race_time
                FROM race_results
                WHERE race_number LIKE ?
                OR name LIKE ?
                ORDER BY race_time ASC
                """,
                (
                    f"%{search_text}%",
                    f"%{search_text}%"
                )
            ).fetchall()

        if not results:
            QMessageBox.information(
                self,
                "Search Result",
                "No race result found."
            )
            self.loadRaceResults()
            return

        self.openMenTable.setRowCount(0)
        self.openWomenTable.setRowCount(0)
        self.seniorCitizenMenTable.setRowCount(0)
        self.seniorCitizenWomenTable.setRowCount(0)

        category_tables = {
            "Open Men": self.openMenTable,
            "Open Women": self.openWomenTable,
            "Senior Citizen Men": self.seniorCitizenMenTable,
            "Senior Citizen Women": self.seniorCitizenWomenTable
        }

        category_results = {
            "Open Men": [],
            "Open Women": [],
            "Senior Citizen Men": [],
            "Senior Citizen Women": []
        }

        for result in results:
            race_number, name, category, distance, race_time = result

            if category in category_results:
                category_results[category].append(result)

        for category, records in category_results.items():

            table = category_tables[category]

            for rank, record in enumerate(records, start=1):

                race_number, name, category, distance, race_time = record

                row = table.rowCount()
                table.insertRow(row)

                if rank == 1:
                    rank_text = "1st"
                elif rank == 2:
                    rank_text = "2nd"
                elif rank == 3:
                    rank_text = "3rd"
                else:
                    rank_text = f"{rank}th"

                table.setItem(row, 0, QTableWidgetItem(rank_text))
                table.setItem(row, 1, QTableWidgetItem(race_number))
                table.setItem(row, 2, QTableWidgetItem(name))
                table.setItem(row, 3, QTableWidgetItem(distance))
                table.setItem(row, 4, QTableWidgetItem(race_time))

    def searchTextChanged(self):
        if not self.searchLineEdit.text().strip():
            self.loadRaceResults()

    def clearFields(self):
        self.rankLineEdit.clear()
        self.raceNumberLineEdit.clear()
        self.fullNameLineEdit.clear()
        self.categoryComboBox.setCurrentIndex(0)
        self.distanceComboBox.setCurrentIndex(0)
        self.raceTimeLineEdit.clear()