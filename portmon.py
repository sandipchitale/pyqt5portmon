import sys
from os import environ
from sys import platform

from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QMouseEvent, QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QSizePolicy,
                             QToolBar, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QCheckBox, QLabel,
                             QHeaderView, QMessageBox, QHBoxLayout)

from netstat import Netstat, NetstatRecord


class ForegroundWidget(QWidget):
    def __init__(self, mainWindow: QMainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.dragging = False
        self.prevX = -1
        self.prevY = -1

    def mousePressEvent(self, e: QMouseEvent):
        super().mousePressEvent(e)
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.prevX = e.globalX()
            self.prevY = e.globalY()

    def mouseMoveEvent(self, e: QMouseEvent):
        super().mouseMoveEvent(e)
        if self.dragging:
            deltaX = e.globalX() - self.prevX
            deltaY = e.globalY() - self.prevY
            self.mainWindow.move(self.mainWindow.x() + deltaX, self.mainWindow.y() + deltaY)
            self.prevX = e.globalX()
            self.prevY = e.globalY()

    def mouseReleaseEvent(self, e: QMouseEvent):
        super().mouseReleaseEvent(e)
        if e.button() == Qt.LeftButton:
            self.dragging = False


class MainWindow(QMainWindow):
    COLUMN_HEADERS = ("Local Address", "Local Port", "Foreign Address", "Foreign Port", "State", "PID", "Kill")

    def __init__(self):
        super().__init__()
        self.netstatTable = QTableWidget()

        # preload background image pixmap
        self.backgroundImage = QPixmap("assets/portmon-tablet.png")
        self.setGeometry(300, 100, self.backgroundImage.size().width(), self.backgroundImage.size().height())
        self.setWindowOpacity(0.0)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.exitButton = QPushButton("⨉")

        user = environ.get("USER")
        if platform == "linux" and "root" != user:
            self.netstatTable.setToolTip(f"On process ids owned by user '{user}' are available. Maybe run as sudo.")

        self.ports = QLineEdit()

        self.netstatRecordsCount = QLabel("  Count: 0")

        self.close_wait = QCheckBox("CLOSE_WAIT    ")
        self.close_wait.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.close_wait.clicked.connect(lambda: self.refresh())

        self.established = QCheckBox("ESTABLISHED    ")
        self.established.setChecked(True)
        # noinspection PyUnresolvedReferences
        self.established.clicked.connect(lambda: self.refresh())

        self.listen = QCheckBox("LISTEN    ")
        self.listen.setChecked(True)
        # noinspection PyUnresolvedReferences
        self.listen.clicked.connect(lambda: self.refresh())

        self.time_wait = QCheckBox("TIME_WAIT")
        self.time_wait.setChecked(False)
        # noinspection PyUnresolvedReferences
        self.time_wait.clicked.connect(lambda: self.refresh())

        # noinspection PyUnresolvedReferences
        self.ports.returnPressed.connect(lambda: self.refresh())
        self.netstat = Netstat()
        self.setWindowTitle("Port Monitor")
        self.setGeometry(500, 100, 900, 600)
        self.initUI()
        self.refresh()

    def initUI(self):
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        centralWidgetGridLayout = QGridLayout()
        centralWidget.setLayout(centralWidgetGridLayout)

        # Background label
        backgroundLabel = QLabel("iaconsole", self)
        backgroundLabel.setPixmap(self.backgroundImage)
        # add in cell 0,0
        centralWidgetGridLayout.addWidget(backgroundLabel, 0, 0)

        # Main Panel
        foregroundWidget = ForegroundWidget(self)
        centralWidgetGridLayout.addWidget(foregroundWidget, 0, 0)

        foregroundWidget.setMouseTracking(True)
        foregroundWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        foregroundWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        foregroundWidgetLayout = QVBoxLayout()
        foregroundWidget.setLayout(foregroundWidgetLayout)

        foregroundWidgetLayout.setContentsMargins(21, 22, 21, 50)
        foregroundWidgetLayout.setSpacing(0)
        foregroundWidgetLayout.setStretch(0, 0)

        primaryTitlebar = QWidget()
        foregroundWidgetLayout.addWidget(primaryTitlebar)

        primaryTitlebarLayout = QHBoxLayout()
        primaryTitlebar.setLayout(primaryTitlebarLayout)
        primaryTitlebarLayout.setSpacing(4)

        # logo = QLabel()
        # logo.setPixmap(QIcon("icons/port.png").pixmap(20, 20))
        # primaryTitlebarLayout.addWidget(logo)
        # logo.setStyleSheet("margin-left: 10px;")

        logoLabel = QLabel("Port Monitor")
        primaryTitlebarLayout.addWidget(logoLabel)
        logoLabel.setStyleSheet("margin-left: 3px; font-size: 20px; font-weight: bold; color: #333;")

        primaryTitlebarLayout.addStretch(1)

        self.exitButton.setStyleSheet("border-radius: 14px; border: 1 solid #bbb; padding: 6px 10px;")
        # noinspection PyUnresolvedReferences
        self.exitButton.clicked.connect(lambda: sys.exit(0))
        primaryTitlebarLayout.addWidget(self.exitButton)

        primaryToolbar = QWidget()
        foregroundWidgetLayout.addWidget(primaryToolbar)

        primaryToolbarLayout = QHBoxLayout()
        primaryToolbar.setLayout(primaryToolbarLayout)
        primaryToolbarLayout.setSpacing(4)

        portsLabel = QLabel("Ports filter:")
        # portsLabel.setPixmap(QIcon("icons/port.png").pixmap(20, 20))
        portsLabel.setToolTip("Specify comma separated list of ports to show. e.g. 8080,9090")
        primaryToolbarLayout.addWidget(portsLabel)

        primaryToolbarLayout.addWidget(self.ports)
        self.ports.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        refreshButton = QPushButton()
        refreshButton.setIcon(QIcon("icons/refresh.png"))
        refreshButton.setIconSize(QSize(20, 20))
        # noinspection PyUnresolvedReferences
        refreshButton.clicked.connect(self.refresh)
        primaryToolbarLayout.addWidget(refreshButton)

        secondaryToolbar = QToolBar()
        foregroundWidgetLayout.addWidget(secondaryToolbar)

        secondaryToolbar.addWidget(self.netstatRecordsCount)

        stretcher = QLabel("")
        stretcher.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        secondaryToolbar.addWidget(stretcher)

        secondaryToolbar.addWidget(QLabel("States:    "))
        secondaryToolbar.addWidget(self.close_wait)
        secondaryToolbar.addWidget(self.established)
        secondaryToolbar.addWidget(self.listen)
        secondaryToolbar.addWidget(self.time_wait)

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
        self.netstatTable.setColumnWidth(6, 20)

        self.netstatTable.setHorizontalHeaderLabels(MainWindow.COLUMN_HEADERS)

        for i in [1, 3, 5]:
            headerItem = self.netstatTable.horizontalHeaderItem(i)
            headerItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

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

    @staticmethod
    def killProcess(pid):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle(" ")
        msg.setText(f"Kill: {pid} ?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        if msg.exec_() == QMessageBox.Ok:
            print(f"Killing: {pid}.")

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
            self.netstatRecordsCount.setText(f"Count: {len(netstatRecords)}")
            for row, netstatRecord in enumerate(sorted(netstatRecords, key=lambda nsr: nsr.localPort)):
                self.netstatTable.setItem(row, 0, QTableWidgetItem(netstatRecord.localAddress))
                localPortItem = QTableWidgetItem(str(netstatRecord.localPort))
                localPortItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.netstatTable.setItem(row, 1, localPortItem)
                self.netstatTable.setItem(row, 2, QTableWidgetItem(netstatRecord.foreignAddress))
                foreignPortItem = QTableWidgetItem(netstatRecord.foreignPort)
                foreignPortItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.netstatTable.setItem(row, 3, foreignPortItem)
                self.netstatTable.setItem(row, 4, QTableWidgetItem(netstatRecord.state))
                pidItem = QTableWidgetItem(netstatRecord.pid)
                pidItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.netstatTable.setItem(row, 5, pidItem)
                if netstatRecord.pid != "-":
                    killPidButton = QPushButton("")
                    killPidButton.setIcon(QIcon("icons/killpid.png"))
                    killPidButton.setIconSize(QSize(20, 20))
                    killPidButton.setStyleSheet("border: 0 solid #bbb; width: 20px;")
                    self.netstatTable.setCellWidget(row, 6, killPidButton)
                    def make_lambda(pid):
                        return lambda ev: MainWindow.killProcess(pid)
                    # noinspection PyUnresolvedReferences
                    killPidButton.clicked.connect(make_lambda(netstatRecord.pid))
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
