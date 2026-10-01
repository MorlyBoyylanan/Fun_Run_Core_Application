import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer, QTime
from database.database import Database


class RaceTimerPage(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("features/raceTimerFrontPage/raceTimerUi.ui",self)

        background_image_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "background", "FirstBackground.png")
        
        background_image_path = os.path.abspath(background_image_path)  
        background_image_path = background_image_path.replace( "\\", "/")
        
        self.database = Database()
        self.timer = QTimer(self)
        self.elapsed_time = 0
        self.is_paused = False

        self.timer.timeout.connect(self.updateTimer)
        self.startbtn.clicked.connect(self.startTimer)
        self.stopbtn.clicked.connect(self.stopTimer)
        self.pausebtn.clicked.connect(self.pauseTimer)
        self.recordBtn.clicked.connect(self.recordResult)
        self.raceNumberLineedit.textChanged.connect(self.findParticipant)

    
    def updateTimer(self):
        elapsed = self.start_time.msecsTo(QTime.currentTime())

        hours = elapsed // 3600000
        minutes = (elapsed // 60000) % 60
        seconds = (elapsed // 1000) % 60
        milliseconds = (elapsed % 1000) // 10

        self.timerLabel.setText(
            f"{hours:02d}:{minutes:02d}:{seconds:02d}:{milliseconds:02d}"
        )

    def startTimer(self):
        if self.is_paused:
            self.start_time = QTime.currentTime().addMSecs(-self.elapsed_time)
            self.is_paused = False
        else:
            self.start_time = QTime.currentTime()
            self.elapsed_time = 0

        self.timer.start(10)
        self.timerLabel.setStyleSheet("color: #28A745;")

    def stopTimer(self):
        if self.timer.isActive():
            self.elapsed_time = self.start_time.msecsTo(QTime.currentTime())
            self.timer.stop()

            self.is_paused = False
            self.timerLabel.setStyleSheet("color: #F0AD4E;")

    def pauseTimer(self):
        if self.timer.isActive():
            self.elapsed_time = self.start_time.msecsTo(QTime.currentTime())
            self.timer.stop()

            self.is_paused = True
            self.timerLabel.setStyleSheet("color: #1E73BE;")

    def findParticipant(self):
        race_number = self.raceNumberLineedit.text().strip()

        if not race_number:
            self.fullNameLineEdit.clear()
            self.categoryLineEdit.clear()
            self.distanceLineEdit.clear()
            return

        participant = self.database.get_participant_by_race_number(race_number)

        if participant:
            name, category, distance = participant

            self.fullNameLineEdit.setText(name)
            self.categoryLineEdit.setText(category)
            self.distanceLineEdit.setText(distance)
        else:
            self.fullNameLineEdit.clear()
            self.categoryLineEdit.clear()
            self.distanceLineEdit.clear()
                

    def recordResult(self):
        race_number = self.raceNumberLineedit.text().strip()
        name = self.fullNameLineEdit.text().strip()
        category = self.categoryLineEdit.text().strip()
        distance = self.distanceLineEdit.text().strip()

        race_time = self.timerLabel.text()

        success = self.database.save_race_result(
            race_number,
            name,
            category,
            distance,
            race_time
        )

        if not success:
            QMessageBox.warning(
                self,
                "Already Recorded",
                f"Race Number {race_number} has already been recorded."
            )
            return

        print("Race Result Recorded:")
        print("Race Number:", race_number)
        print("Name:", name)
        print("Category:", category)
        print("Distance:", distance)
        print("Race Time:", race_time)

        self.raceNumberLineedit.clear()
        self.fullNameLineEdit.clear()
        self.categoryLineEdit.clear()
        self.distanceLineEdit.clear()