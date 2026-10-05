from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox

from features.registrationFrontPage.registrationPage import RegistrationPage
from features.raceTimerFrontPage.raceTimerPage import RaceTimerPage
from features.participantsDataRecordFrontPage.participantsDataRecordPage import ParticipantsDataRecordPage
from features.singletManagementFrontPage.singletManagementPage import SingletManagementPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Set the main window title
        self.setWindowTitle("Fun Run Core Application")

        # Set the main window size
        self.resize(1650, 1000)

        # Create the pages
        self.registrationpage = RegistrationPage()
        self.racetimerpage = RaceTimerPage()
        self.participantdatarecordpage = ParticipantsDataRecordPage()
        self.singletmanagementpage = SingletManagementPage()
        # Create the tabs
        self.tabs = QTabWidget()

        # Add pages to tabs
        self.tabs.addTab(self.registrationpage,"Registration Page")
        self.tabs.addTab(self.racetimerpage, "Race Timer Page")
        self.tabs.addTab(self.participantdatarecordpage, "Participants Data Record Page")
        self.tabs.addTab(self.singletmanagementpage, "Singlet Management Page")

        # Refresh Participant Data Record when its tab is opened
        self.tabs.currentChanged.connect(self.refreshPage)

        # Set the tabs as the central widget
        self.setCentralWidget(self.tabs)

    def refreshPage(self, index):

        if index == self.tabs.indexOf(self.participantdatarecordpage):
            self.participantdatarecordpage.loadRaceResults()

        if index == self.tabs.indexOf(self.singletmanagementpage):
            self.singletmanagementpage.loadRecords()

    def closeEvent(self, event):

        if self.racetimerpage.timer.isActive():

            reply = QMessageBox.question(
                self,
                "Timer Still Running",
                "The timer is still running.\n\n"
                "Do you want to stop the timer and exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.racetimerpage.stopTimer()
                event.accept()
            else:
                event.ignore()

        else:
            event.accept()