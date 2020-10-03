import signal
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2 import QtCore
import pyqtgraph as pg


class UiLoader(QUiLoader):
    def createWidget(self, className, parent=None, name=""):
        if className == "PlotWidget":
            return pg.PlotWidget(parent=parent)
        return super().createWidget(className, parent, name)


class AppMainWindow(QtCore.QObject):
    def __init__(self):
        super().__init__()
        uiFile = QtCore.QFile("ui/MainWindow.ui")
        loader = UiLoader()
        self.window = loader.load(uiFile)
        uiFile.close()
        self.settings = QtCore.QSettings("AlonsoProjects", "InvPendulum")
        self.window.BaudRate.valueChanged.connect(self.newBaudRate)
        self.window.SerialPort.editingFinished.connect(self.newSerialPort)
        self.setupWidgets()

    def setupWidgets(self):
        """ Set up widgets from saved data."""
        baudRate = int(self.settings.value("baudRate"))
        serialPort = self.settings.value("serialPort")
        self.window.BaudRate.setValue(baudRate)
        self.window.SerialPort.setText(serialPort)

    def setupPlots(self):
        pass

    def newBaudRate(self):
        """ Saves a new baud rate."""
        baudRate = self.window.BaudRate.value()
        self.settings.setValue("baudRate", baudRate)

    def newSerialPort(self):
        """ Saves a new serial port."""
        serialPort = self.window.SerialPort.text()
        self.settings.setValue("serialPort", serialPort)


if __name__ == "__main__":
    # Used here in order to get ability to ctrl+c to close program
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)

    MainWindow = AppMainWindow()
    MainWindow.window.show()

    sys.exit(app.exec_())
