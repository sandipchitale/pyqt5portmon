# PyQt5 introduction
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QSizePolicy,
                             QToolBar, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QCheckBox, QLabel,
                             QHeaderView)

from netstat import Netstat, NetstatRecord


class ForegroundWidget(QWidget):
    def __init__(self, mainWindow: QMainWindow):
        super().__init__()
        self.mainWindow = mainWindow

class MainWindow(QMainWindow):
    COLUMN_HEADERS =  ("Local Address", "Local Port", "Foreign Address", "Foreign Port", "State", "PID", "Actions")

    def __init__(self):
        super().__init__()
        self.netstatTable = QTableWidget()

        self.ports = QLineEdit()

        self.close_wait = QCheckBox("CLOSE_WAIT")
        self.close_wait.setChecked(False)

        self.established = QCheckBox("ESTABLISHED")
        self.established.setChecked(True)

        self.listen = QCheckBox("LISTEN")
        self.listen.setChecked(True)

        self.time_wait = QCheckBox("TIME_WAIT")
        self.time_wait.setChecked(False)

        # noinspection PyUnresolvedReferences
        self.ports.returnPressed.connect(lambda : self.refresh())
        self.netstat = Netstat()
        self.setWindowTitle("iaconsole")
        self.setGeometry(500, 100, 645, 600)
        self.initUI()
        self.refresh()

    def initUI(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        centralWidgetGridLayout = QGridLayout()
        centralWidget.setLayout(centralWidgetGridLayout)

        # Main Panel
        foregroundWidget = ForegroundWidget(self)

        foregroundWidgetLayout = QVBoxLayout()
        foregroundWidget.setLayout(foregroundWidgetLayout)

        centralWidgetGridLayout.addWidget(foregroundWidget, 0, 0)
        foregroundWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        foregroundWidgetLayout.setContentsMargins(0,0,0,0)
        foregroundWidgetLayout.setSpacing(0)

        primaryToolbar = QToolBar()
        foregroundWidgetLayout.addWidget(primaryToolbar)

        primaryToolbarLayout = primaryToolbar.layout()
        primaryToolbarLayout.setSpacing(4)

        primaryToolbar.addWidget(self.ports)
        self.ports.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        refreshButton = QPushButton("↻")
        # noinspection PyUnresolvedReferences
        refreshButton.clicked.connect(self.refresh)
        primaryToolbar.addWidget(refreshButton)

        foregroundWidgetLayout.setStretch(0, 0)

        statesToolbar = QToolBar()
        foregroundWidgetLayout.addWidget(statesToolbar)

        statesToolbar.addWidget(self.close_wait)

        stretcher = QLabel("")
        stretcher.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        statesToolbar.addWidget(stretcher)

        statesToolbar.addWidget(self.established)

        stretcher = QLabel("")
        stretcher.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        statesToolbar.addWidget(stretcher)

        statesToolbar.addWidget(self.listen)

        stretcher = QLabel("")
        stretcher.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        statesToolbar.addWidget(stretcher)

        statesToolbar.addWidget(self.time_wait)

        foregroundWidgetLayout.setStretch(1, 0)

        self.netstatTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        foregroundWidgetLayout.addWidget(self.netstatTable)

        self.netstatTable.setColumnCount(7)
        self.netstatTable.setColumnWidth(0, 110)
        self.netstatTable.setColumnWidth(1, 80)
        self.netstatTable.setColumnWidth(2, 110)
        self.netstatTable.setColumnWidth(3, 80)
        self.netstatTable.setColumnWidth(4, 100)
        self.netstatTable.setColumnWidth(5, 80)
        self.netstatTable.setColumnWidth(6, 50)

        self.netstatTable.setHorizontalHeaderLabels(MainWindow.COLUMN_HEADERS)
        self.netstatTable.verticalHeader().setVisible(False)

        self.netstatTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.netstatTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.netstatTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.netstatTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        foregroundWidgetLayout.setStretch(2, 1)

    def applyStateFilters(self, netstatRecords: list[NetstatRecord]):
        return [nsr for nsr in netstatRecords if
                ("CLOSE_WAIT" == nsr.state and self.close_wait.isChecked()) or
                ("ESTABLISHED" == nsr.state and self.established.isChecked()) or
                ("LISTEN" == nsr.state and self.listen.isChecked()) or
                ("TIME_WAIT" == nsr.state and self.time_wait.isChecked())]

    def killProcess(self, pid):
        print(f"Killing process with PID: {pid}")

    def refresh(self):
        self.netstatTable.setRowCount(0)
        try:
            ports = [int(port) for port in self.ports.text().split(",") if port and str.isdigit(port.strip())]
            netstatRecords = self.netstat.netstat()
            if len(ports) > 0:
                netstatRecords = list(filter(lambda nsr: nsr.localPort in ports, netstatRecords))
            netstatRecords = self.applyStateFilters(netstatRecords)
            netstatRecords = sorted(netstatRecords, key=lambda nsr: nsr.localPort)

            self.netstatTable.setRowCount(len(netstatRecords))
            row = 0
            for netstatRecord in sorted(netstatRecords, key=lambda nsr: nsr.localPort):
                self.netstatTable.setItem(row, 0, QTableWidgetItem(netstatRecord.localAddress))
                localPortItem = QTableWidgetItem(str(netstatRecord.localPort))
                localPortItem.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                self.netstatTable.setItem(row, 1, localPortItem)
                self.netstatTable.setItem(row, 2, QTableWidgetItem(netstatRecord.foreignAddress))
                foreignPortItem = QTableWidgetItem(netstatRecord.foreignPort)
                foreignPortItem.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                self.netstatTable.setItem(row, 3, foreignPortItem)
                self.netstatTable.setItem(row, 4, QTableWidgetItem(netstatRecord.state))
                pidItem = QTableWidgetItem(netstatRecord.pid)
                pidItem.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                self.netstatTable.setItem(row, 5, pidItem)
                if netstatRecord.pid != "-":
                    killPidButton = QPushButton("⨉")
                    self.netstatTable.setCellWidget(row, 6, killPidButton)
                    def make_lambda(pid):
                        return lambda ev: self.killProcess(pid)
                    # noinspection PyUnresolvedReferences
                    killPidButton.clicked.connect(make_lambda(netstatRecord.pid))
                row += 1
        except ChildProcessError as cpe:
            print(cpe)
        except BaseException as be:
            print(be)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
