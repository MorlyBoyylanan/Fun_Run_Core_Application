
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from PyQt5.QtGui import QColor

from database.database import Database


class SingletManagementPage(QMainWindow):

    def __init__(self):
        super().__init__()

        uic.loadUi(
            "features/singletManagementFrontPage/singletManagement.ui",
            self
        )

        # Background image
        background_image_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "background",
            "FourthBackground.png"
        )

        background_image_path = os.path.abspath(background_image_path)
        background_image_path = background_image_path.replace("\\", "/")

        self.setObjectName("singletManagementPagebg")

        self.setStyleSheet(f"""
        QWidget#singletManagementPagebg {{
            border-image: url("{background_image_path}")
            1 0 0 0 stretch stretch;
        }}
        """)

        # Database
        self.database = Database()

        # Migrate the old table if it still has payment_status
        self.migrateSingletTable()

        self.raceNumberLineEdit.setReadOnly(True)

        # Button connections
        self.createButton.clicked.connect(self.createRecord)
        self.updateButton.clicked.connect(self.updateRecord)
        self.deleteButton.clicked.connect(self.deleteRecord)
        self.searchButton.clicked.connect(self.searchRecord)
        self.searchLineEdit.textChanged.connect(self.searchTextChanged)
        self.clearButton.clicked.connect(self.clearField)
        self.singletTable.cellClicked.connect(self.selectRecord)

        self.loadRecords()

    # Remove the old payment_status column while preserving existing records
    def migrateSingletTable(self):
        with self.database.connect() as connection:
            columns = connection.execute(
                "PRAGMA table_info(singlet_records)"
            ).fetchall()

            column_names = [column[1] for column in columns]

            if not columns:
                connection.execute(
                    """
                    CREATE TABLE singlet_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        race_number TEXT,
                        name TEXT NOT NULL,
                        category TEXT,
                        distance TEXT,
                        cpnumber TEXT,
                        singlet_size TEXT NOT NULL,
                        singlet_status TEXT NOT NULL
                    )
                    """
                )
                return

            if "payment_status" in column_names:
                connection.execute(
                    """
                    CREATE TABLE singlet_records_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        race_number TEXT,
                        name TEXT NOT NULL,
                        category TEXT,
                        distance TEXT,
                        cpnumber TEXT,
                        singlet_size TEXT NOT NULL,
                        singlet_status TEXT NOT NULL
                    )
                    """
                )

                connection.execute(
                    """
                    INSERT INTO singlet_records_new
                    (
                        id, race_number, name, category, distance,
                        cpnumber, singlet_size, singlet_status
                    )
                    SELECT
                        id, race_number, name, category, distance,
                        cpnumber, singlet_size, singlet_status
                    FROM singlet_records
                    """
                )

                connection.execute("DROP TABLE singlet_records")
                connection.execute(
                    "ALTER TABLE singlet_records_new RENAME TO singlet_records"
                )

    # Create singlet record
    def createRecord(self):
        race_number = self.raceNumberLineEdit.text().strip()
        name = self.fullNameLineEdit.text().strip()
        category = self.categoryComboBox.currentText()
        distance = self.distanceComboBox.currentText()
        cpnumber = self.contactNumberLineEdit.text().strip()
        singlet_size = self.singletSizeComboBox.currentText()
        singlet_status = self.singletStatusComboBox.currentText()

        if not name or not singlet_size or not singlet_status:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please complete the required singlet information."
            )
            return

        # If the record has a race number, ensure the participant is registered
        if race_number:
            participant = self.database.get_participant_by_race_number(
                race_number
            )

            if not participant:
                QMessageBox.warning(
                    self,
                    "Participant Not Found",
                    "This race number is not registered."
                )
                return

            name, category, distance = participant

        with self.database.connect() as connection:
            if race_number:
                existing = connection.execute(
                    """
                    SELECT id
                    FROM singlet_records
                    WHERE race_number = ?
                    """,
                    (race_number,)
                ).fetchone()

                if existing:
                    QMessageBox.warning(
                        self,
                        "Record Exists",
                        "A singlet record already exists for this race number. "
                        "Please select it and use Update."
                    )
                    return

            connection.execute(
                """
                INSERT INTO singlet_records
                (
                    race_number, name, category, distance,
                    cpnumber, singlet_size, singlet_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    race_number,
                    name,
                    category,
                    distance,
                    cpnumber,
                    singlet_size,
                    singlet_status
                )
            )

        QMessageBox.information(
            self,
            "Success",
            "Singlet record created successfully."
        )

        self.clearField()
        self.loadRecords()

    # Color rows according to singlet status
    def colorRow(self, row):
        status_item = self.singletTable.item(row, 6)

        if not status_item:
            return

        singlet_status = status_item.text()

        colors = {
            "Released": QColor("#D4EDDA"),
            "Paid": QColor("#D1ECF1"),
            "Reserved": QColor("#FFF3CD"),
            "Not Paid": QColor("#F8D7DA"),
            "Cancelled": QColor("#E2E3E5")
        }

        color = colors.get(singlet_status, QColor("#FFFFFF"))

        for column in range(self.singletTable.columnCount()):
            item = self.singletTable.item(row, column)

            if item:
                item.setBackground(color)

    # Update selected singlet record
    def updateRecord(self):
        race_number = self.raceNumberLineEdit.text().strip()
        name = self.fullNameLineEdit.text().strip()
        category = self.categoryComboBox.currentText()
        distance = self.distanceComboBox.currentText()
        cpnumber = self.contactNumberLineEdit.text().strip()
        singlet_size = self.singletSizeComboBox.currentText()
        singlet_status = self.singletStatusComboBox.currentText()

        if not name:
            QMessageBox.warning(
                self,
                "No Record Selected",
                "Please select a singlet record first."
            )
            return

        if race_number:
            participant = self.database.get_participant_by_race_number(
                race_number
            )

            if not participant:
                QMessageBox.warning(
                    self,
                    "Participant Not Found",
                    "This race number is not registered."
                )
                return

            name, category, distance = participant

        with self.database.connect() as connection:
            if race_number:
                cursor = connection.execute(
                    """
                    UPDATE singlet_records
                    SET
                        name = ?,
                        category = ?,
                        distance = ?,
                        cpnumber = ?,
                        singlet_size = ?,
                        singlet_status = ?
                    WHERE race_number = ?
                    """,
                    (
                        name,
                        category,
                        distance,
                        cpnumber,
                        singlet_size,
                        singlet_status,
                        race_number
                    )
                )
            else:
                cursor = connection.execute(
                    """
                    UPDATE singlet_records
                    SET
                        name = ?,
                        category = ?,
                        distance = ?,
                        cpnumber = ?,
                        singlet_size = ?,
                        singlet_status = ?
                    WHERE name = ?
                    AND cpnumber = ?
                    AND (race_number = '' OR race_number IS NULL)
                    """,
                    (
                        name,
                        category,
                        distance,
                        cpnumber,
                        singlet_size,
                        singlet_status,
                        name,
                        cpnumber
                    )
                )

            if cursor.rowcount == 0:
                QMessageBox.warning(
                    self,
                    "Record Not Found",
                    "No matching singlet record was found."
                )
                return

        QMessageBox.information(
            self,
            "Updated",
            "Singlet information updated successfully."
        )

        self.clearField()
        self.loadRecords()

    # Delete selected singlet record
    def deleteRecord(self):
        race_number = self.raceNumberLineEdit.text().strip()
        name = self.fullNameLineEdit.text().strip()
        cpnumber = self.contactNumberLineEdit.text().strip()

        if not name:
            QMessageBox.warning(self, "No Record Selected", "Please select a singlet record first.")
            return

        reply = QMessageBox.question(self,"Delete Record", f"Are you sure you want to delete the singlet record for {name}?",QMessageBox.Yes | QMessageBox.No,QMessageBox.No)

        if reply == QMessageBox.No:
            return

        with self.database.connect() as connection:
            if race_number:
                connection.execute(
                    """
                    DELETE FROM singlet_records
                    WHERE race_number = ?
                    """,
                    (race_number,)
                )
            else:
                connection.execute(
                    """
                    DELETE FROM singlet_records
                    WHERE (race_number = '' OR race_number IS NULL)
                    AND name = ?
                    AND cpnumber = ?
                    """,
                    (name, cpnumber)
                )

        QMessageBox.information(self,"Deleted","Singlet record deleted successfully.")

        self.clearField()
        self.loadRecords()

    # Search participant and singlet records
    def searchRecord(self):
        search_text = self.searchLineEdit.text().strip()

        if not search_text:
            self.loadRecords()
            return

        self.singletTable.setRowCount(0)

        with self.database.connect() as connection:
            participants = connection.execute(
                """
                SELECT
                    p.race_number,
                    p.name,
                    p.category,
                    p.distance,
                    p.cpnumber,
                    COALESCE(s.singlet_size, 'Not Selected'),
                    COALESCE(s.singlet_status, 'Reserved')
                FROM participants p
                LEFT JOIN singlet_records s
                    ON p.race_number = s.race_number
                WHERE p.race_number LIKE ?
                   OR p.name LIKE ?
                """,
                (
                    f"%{search_text}%",
                    f"%{search_text}%"
                )
            ).fetchall()

            singlet_only = connection.execute(
                """
                SELECT
                    race_number,
                    name,
                    category,
                    distance,
                    cpnumber,
                    singlet_size,
                    singlet_status
                FROM singlet_records
                WHERE (race_number = '' OR race_number IS NULL)
                AND name LIKE ?
                """,
                (f"%{search_text}%",)
            ).fetchall()

        records = participants + singlet_only

        if not records:
            QMessageBox.information(self,  "Search Result", "No participant found.")
            self.loadRecords()
            return

        for record in records:
            row = self.singletTable.rowCount()
            self.singletTable.insertRow(row)

            for column, value in enumerate(record):
                self.singletTable.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(value) if value is not None else ""
                    )
                )

            self.colorRow(row)

    # Load all participants and singlet-only records
    def loadRecords(self):
        self.singletTable.setRowCount(0)

        with self.database.connect() as connection:
            participants = connection.execute(
                """
                SELECT
                    p.race_number,
                    p.name,
                    p.category,
                    p.distance,
                    p.cpnumber,
                    COALESCE(s.singlet_size, 'Not Selected'),
                    COALESCE(s.singlet_status, 'Reserved')
                FROM participants p
                LEFT JOIN singlet_records s
                    ON p.race_number = s.race_number
                """
            ).fetchall()

            singlet_only = connection.execute(
                """
                SELECT
                    race_number,
                    name,
                    category,
                    distance,
                    cpnumber,
                    singlet_size,
                    singlet_status
                FROM singlet_records
                WHERE race_number = ''
                   OR race_number IS NULL
                """
            ).fetchall()

        records = participants + singlet_only

        for record in records:
            row = self.singletTable.rowCount()
            self.singletTable.insertRow(row)

            for column, value in enumerate(record):
                self.singletTable.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(value) if value is not None else ""
                    )
                )

            self.colorRow(row)

    # Reload all records when search is cleared
    def searchTextChanged(self):
        if not self.searchLineEdit.text().strip():
            self.loadRecords()

    # Load selected record into fields
    def selectRecord(self, row, column):
        race_number_item = self.singletTable.item(row, 0)
        name_item = self.singletTable.item(row, 1)
        category_item = self.singletTable.item(row, 2)
        distance_item = self.singletTable.item(row, 3)
        cpnumber_item = self.singletTable.item(row, 4)
        size_item = self.singletTable.item(row, 5)
        status_item = self.singletTable.item(row, 6)

        race_number = race_number_item.text() if race_number_item else ""
        name = name_item.text() if name_item else ""
        category = category_item.text() if category_item else ""
        distance = distance_item.text() if distance_item else ""
        cpnumber = cpnumber_item.text() if cpnumber_item else ""
        singlet_size = size_item.text() if size_item else "Not Selected"
        singlet_status = status_item.text() if status_item else "Reserved"

        self.raceNumberLineEdit.setText(race_number)
        self.fullNameLineEdit.setText(name)
        self.categoryComboBox.setCurrentText(category)
        self.distanceComboBox.setCurrentText(distance)
        self.contactNumberLineEdit.setText(cpnumber)
        self.singletSizeComboBox.setCurrentText(singlet_size)
        self.singletStatusComboBox.setCurrentText(singlet_status)

    # Clear input fields
    def clearField(self):
        self.raceNumberLineEdit.clear()
        self.fullNameLineEdit.clear()
        self.categoryComboBox.setCurrentIndex(0)
        self.distanceComboBox.setCurrentIndex(0)
        self.contactNumberLineEdit.clear()
        self.singletSizeComboBox.setCurrentIndex(0)
        self.singletStatusComboBox.setCurrentIndex(0)
