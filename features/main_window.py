from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox

from features.registrationFrontPage.registrationPage import RegistrationPage
from features.raceTimerFrontPage.raceTimerPage import RaceTimerPage

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Set the main window title
        self.setWindowTitle("Fun Run Core Application")

        # Set the main window size
        self.resize(1650, 900)

        # Create the Registration Page
        self.registrationpage = RegistrationPage()
        self.racetimerpage = RaceTimerPage()

        # Create the tabs
        self.tabs = QTabWidget()

        # Add Registration Page
        self.tabs.addTab(self.registrationpage,"Registration Page")
        self.tabs.addTab(self.racetimerpage,"Race Timer Page ")

        # Set the tabs as the central widget
        self.setCentralWidget(self.tabs)

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