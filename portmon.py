# PyQt5 introduction
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QSizePolicy,
                             QToolBar, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem)

from netstat import Netstat


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

        refreshButton = QPushButton("Refresh")
        refreshButton.clicked.connect(self.refresh)
        primaryToolbar.addWidget(refreshButton)

        foregroundWidgetLayout.setStretch(0, 0)

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

        self.netstatTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.netstatTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        foregroundWidgetLayout.setStretch(1, 1)

    def refresh(self):
        self.netstatTable.setRowCount(0)
        try:
            ports = [int(port) for port in self.ports.text().split(",") if port and str.isdigit(port.strip())]
            netstatRecords = sorted(self.netstat.netstat(), key=lambda nsr: nsr.localPort)
            if len(ports) > 0:
                netstatRecords = tuple(filter(lambda nsr: nsr.localPort in ports, netstatRecords))
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
                self.netstatTable.setItem(row, 6, QTableWidgetItem("Delete"))
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
