
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox
from database.database import Database


class ParticipantsDataRecordPage(QMainWindow):

    def __init__(self):
        super().__init__()

        uic.loadUi(
            "features/participantsDataRecordFrontPage/participantsDataRecordUi.ui",
            self
        )

        background_image_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "background", "ThirdBackground.png"
        )

        background_image_path = os.path.abspath(background_image_path)
        background_image_path = background_image_path.replace("\\", "/")

        self.setObjectName("participantDataRecordPagebg")

        self.setStyleSheet(f"""
        QWidget#participantDataRecordPagebg {{
            border-image: url("{background_image_path}")
            0 0 0 0 stretch stretch;
        }}
        """)

        self.database = Database()
        self.selected_race_number = None

        self.searchButton.clicked.connect(self.searchRecord)
        self.searchLineEdit.textChanged.connect(self.searchTextChanged)
        self.deleteButton.clicked.connect(self.deleteRecord)

        self.openMenTable.cellClicked.connect(self.selectRecord)
        self.openWomenTable.cellClicked.connect(self.selectRecord)
        self.seniorCitizenMenTable.cellClicked.connect(self.selectRecord)
        self.seniorCitizenWomenTable.cellClicked.connect(self.selectRecord)

        self.loadRaceResults()

    def getCategoryTables(self):
        return {
            "Open Men": self.openMenTable,
            "Open Women": self.openWomenTable,
            "Senior Citizen Men": self.seniorCitizenMenTable,
            "Senior Citizen Women": self.seniorCitizenWomenTable
        }

    def loadRaceResults(self, search_text=""):
        query = """
            SELECT race_number, name, category, distance, race_time
            FROM race_results
        """

        parameters = ()

        if search_text:
            query += """
                WHERE race_number LIKE ?
                OR name LIKE ?
            """
            parameters = (
                f"%{search_text}%",
                f"%{search_text}%"
            )

        query += " ORDER BY race_time ASC"

        with self.database.connect() as connection:
            results = connection.execute(
                query, parameters
            ).fetchall()

        self.displayRaceResults(results)

    def displayRaceResults(self, results):
        category_tables = self.getCategoryTables()

        for table in category_tables.values():
            table.setRowCount(0)

        category_results = {
            category: [] for category in category_tables
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

                values = [
                    rank_text,
                    race_number,
                    name,
                    distance,
                    race_time
                ]

                for column, value in enumerate(values):
                    table.setItem(
                        row,
                        column,
                        QTableWidgetItem(str(value))
                    )

    def selectRecord(self, row, column):
        table = self.sender()
        item = table.item(row, 1)

        if item:
            self.selected_race_number = item.text()

    def searchRecord(self):
        search_text = self.searchLineEdit.text().strip()

        self.selected_race_number = None

        if not search_text:
            self.loadRaceResults()
            return

        self.loadRaceResults(search_text)

        total_rows = sum(
            table.rowCount()
            for table in self.getCategoryTables().values()
        )

        if total_rows == 0:
            QMessageBox.information(
                self,
                "Search Result",
                "No race result found."
            )
    def searchTextChanged(self):
        if not self.searchLineEdit.text().strip():
            self.selected_race_number = None
            self.loadRaceResults()

    def deleteRecord(self):
        race_number = self.selected_race_number

        if not race_number:
            QMessageBox.warning(
                self,
                "No Record Selected",
                "Please select a race result from one of the tables first."
            )
            return

        reply = QMessageBox.question(
            self,
            "Delete Record",
            f"Are you sure you want to delete "
            f"Race Number {race_number}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        success = self.database.delete_race_result(race_number)

        if success:
            QMessageBox.information(
                self,
                "Deleted",
                "Race result deleted successfully."
            )

            self.selected_race_number = None
            self.loadRaceResults(self.searchLineEdit.text().strip())

        else:
            QMessageBox.warning(
                self,
                "Delete Failed",
                "The race result could not be deleted."
            )
