import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
from PyQt5.QtGui import QColor
from database.database import Database


class SingletManagementPage(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("features/singletManagementFrontPage/singletManagement.ui",self)

        background_image_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "background", "FourthBackground.png")
        
        background_image_path = os.path.abspath(background_image_path)  
        background_image_path = background_image_path.replace( "\\", "/")

        self.setObjectName(
            "singletManagementPagebg"
            )
        
        self.setStyleSheet(f"""
        QWidget#singletManagementPagebg {{
            border-image: url("{background_image_path}")
            1 0 0 0 stretch stretch;
        }}
        """)

        self.database = Database()
        self.raceNumberLineEdit.setReadOnly(True)
        
        self.createButton.clicked.connect(self.createRecord)
        self.updateButton.clicked.connect(self.updateRecord)
        self.deleteButton.clicked.connect(self.deleteRecord)
        self.searchButton.clicked.connect(self.searchRecord)
        self.searchLineEdit.textChanged.connect(self.searchTextChanged)
        self.clearButton.clicked.connect(self.clearField)
        self.singletTable.cellClicked.connect(self.selectRecord)
        
        self.loadRecords()
    

    def createRecord(self):
        race_number = self.raceNumberLineEdit.text().strip()
        name = self.fullNameLineEdit.text().strip()
        category = self.categoryComboBox.currentText()
        distance = self.distanceComboBox.currentText()
        cpnumber = self.contactNumberLineEdit.text().strip()

        singlet_size = self.singletSizeComboBox.currentText()
        singlet_status = self.singletStatusComboBox.currentText()
        payment_status = self.paymentStatusComboBox.currentText()

        if not name or not singlet_size or not singlet_status or not payment_status:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please complete the required singlet information."
            )
            return

        if not race_number:
            category = ""
            distance = ""

        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO singlet_records
                (
                    race_number,
                    name,
                    category,
                    distance,
                    cpnumber,
                    singlet_size,
                    singlet_status,
                    payment_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    race_number,
                    name,
                    category,
                    distance,
                    cpnumber,
                    singlet_size,
                    singlet_status,
                    payment_status
                )
            )

        QMessageBox.information(self, "Success", "Singlet record created successfully.")

        self.clearField()
        self.loadRecords()

    def colorRow(self, row):
        singlet_status = self.singletTable.item(row, 6).text()
        payment_status = self.singletTable.item(row, 7).text()

        if singlet_status == "Purchased" and payment_status == "Paid":
            color = QColor("#D4EDDA")
        else:
            color = QColor("#F8D7DA")

        for column in range(self.singletTable.columnCount()):
            item = self.singletTable.item(row, column)

            if item:
                item.setBackground(color)
    
    def updateRecord(self):
        race_number = self.raceNumberLineEdit.text().strip()
        name = self.fullNameLineEdit.text().strip()
        category = self.categoryComboBox.currentText()
        distance = self.distanceComboBox.currentText()
        cpnumber = self.contactNumberLineEdit.text().strip()

        singlet_size = self.singletSizeComboBox.currentText()
        singlet_status = self.singletStatusComboBox.currentText()
        payment_status = self.paymentStatusComboBox.currentText()

        if not name:
            QMessageBox.warning(self, "No Record Selected", "Please select a singlet record first.")
            return

        with self.database.connect() as connection:

            if race_number:
                connection.execute(
                    """
                    UPDATE singlet_records
                    SET
                        name = ?,
                        category = ?,
                        distance = ?,
                        cpnumber = ?,
                        singlet_size = ?,
                        singlet_status = ?,
                        payment_status = ?
                    WHERE race_number = ?
                    """,
                    (
                        name,
                        category,
                        distance,
                        cpnumber,
                        singlet_size,
                        singlet_status,
                        payment_status,
                        race_number
                    )
                )

            else:
                connection.execute(
                    """
                    UPDATE singlet_records
                    SET
                        name = ?,
                        category = ?,
                        distance = ?,
                        cpnumber = ?,
                        singlet_size = ?,
                        singlet_status = ?,
                        payment_status = ?
                    WHERE name = ?
                    AND (race_number = '' OR race_number IS NULL)
                    """,
                    (
                        name,
                        category,
                        distance,
                        cpnumber,
                        singlet_size,
                        singlet_status,
                        payment_status,
                        name
                    )
                )

        QMessageBox.information(self, "Updated", "Singlet information updated successfully.")

        self.clearField()
        self.loadRecords()

    def deleteRecord(self):
        race_number = self.raceNumberLineEdit.text().strip()
        name = self.fullNameLineEdit.text().strip()
        cpnumber = self.contactNumberLineEdit.text().strip()

        if not name:
            QMessageBox.warning(self, "No Record Selected", "Please select a singlet record first.")
            return

        reply = QMessageBox.question(
            self,
            "Delete Record",
            f"Are you sure you want to delete the singlet record for {name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

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

        QMessageBox.information(self, "Deleted", "Singlet record deleted successfully.")

        self.clearField()
        self.loadRecords()

    def searchRecord(self):
        search_text = self.searchLineEdit.text().strip()

        if not search_text:
            self.loadRecords()
            return

        self.singletTable.setRowCount(0)

        with self.database.connect() as connection:

            # Search registered participants
            participants = connection.execute(
                """
                SELECT
                    p.race_number,
                    p.name,
                    p.category,
                    p.distance,
                    p.cpnumber,
                    COALESCE(s.singlet_size, 'Not Selected'),
                    COALESCE(s.singlet_status, 'Not Purchased'),
                    COALESCE(s.payment_status, 'Not Paid')
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

            # Search singlet-only records
            singlet_only = connection.execute(
                """
                SELECT
                    race_number,
                    name,
                    category,
                    distance,
                    cpnumber,
                    singlet_size,
                    singlet_status,
                    payment_status
                FROM singlet_records
                WHERE (race_number = '' OR race_number IS NULL)
                AND name LIKE ?
                """,
                (f"%{search_text}%",)
            ).fetchall()

        records = participants + singlet_only

        if not records:
            QMessageBox.information(self, "Search Result", "No participant found.")
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
                    COALESCE(s.singlet_status, 'Not Purchased'),
                    COALESCE(s.payment_status, 'Not Paid')
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
                    singlet_status,
                    payment_status
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
                    QTableWidgetItem(str(value) if value is not None else "")
                )
            self.colorRow(row)
    def searchTextChanged(self):
        if not self.searchLineEdit.text().strip():
            self.loadRecords()

    def selectRecord(self, row, column):

        race_number = self.singletTable.item(row, 0).text()
        name = self.singletTable.item(row, 1).text()
        category = self.singletTable.item(row, 2).text()
        distance = self.singletTable.item(row, 3).text()
        cpnumber = self.singletTable.item(row, 4).text()

        self.raceNumberLineEdit.setText(race_number)
        self.fullNameLineEdit.setText(name)
        self.categoryComboBox.setCurrentText(category)
        self.distanceComboBox.setCurrentText(distance)
        self.contactNumberLineEdit.setText(cpnumber)



        with self.database.connect() as connection:
            singlet_record = connection.execute(
                """
                SELECT
                    singlet_size,
                    singlet_status,
                    payment_status
                FROM singlet_records
                WHERE race_number = ?
                """,
                (race_number,)
            ).fetchone()

        if singlet_record:
            singlet_size, singlet_status, payment_status = singlet_record

            self.singletSizeComboBox.setCurrentText(singlet_size)
            self.singletStatusComboBox.setCurrentText(singlet_status)
            self.paymentStatusComboBox.setCurrentText(payment_status)
        else:
            self.singletSizeComboBox.setCurrentIndex(0)
            self.singletStatusComboBox.setCurrentIndex(0)
            self.paymentStatusComboBox.setCurrentIndex(0)

    def clearField(self):
        self.raceNumberLineEdit.clear()
        self.fullNameLineEdit.clear()
        self.categoryComboBox.setCurrentIndex(0)
        self.distanceComboBox.setCurrentIndex(0)
        self.contactNumberLineEdit.clear()
        self.singletSizeComboBox.setCurrentIndex(0)
        self.singletStatusComboBox.setCurrentIndex(0)
        self.paymentStatusComboBox.setCurrentIndex(0)