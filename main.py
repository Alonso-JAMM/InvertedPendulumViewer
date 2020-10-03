import signal
import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2 import QtCore
import pyqtgraph as pg
import numpy as np


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
        self.window.ConnectButton.clicked.connect(self.updatePlot)
        self.setupWidgets()
        self.distancePlot = DistancePlot(self.window.Plot.getPlotItem())
#        self.timer = QtCore.QTimer()
#        self.timer.timeout.connect(self.updatePlot)
#        self.timer.start(700)
        self.i = 0

    def setupWidgets(self):
        """ Set up widgets from saved data."""
        baudRate = int(self.settings.value("baudRate"))
        serialPort = self.settings.value("serialPort")
        self.window.BaudRate.setValue(baudRate)
        self.window.SerialPort.setText(serialPort)

    def newBaudRate(self):
        """ Saves a new baud rate."""
        baudRate = self.window.BaudRate.value()
        self.settings.setValue("baudRate", baudRate)

    def newSerialPort(self):
        """ Saves a new serial port."""
        serialPort = self.window.SerialPort.text()
        self.settings.setValue("serialPort", serialPort)

    def updatePlot(self):
        """ Adds data to the plot"""
        x = self.i
        y = np.sin(self.i)
        self.distancePlot.uptadeData(x, y)
        self.i += 0.1
        self.distancePlot.plot()


class DistancePlot():
    def __init__(self, plotItem):
        self.plotItem = plotItem
        self.setupPlot()
        self.n = 100
        self.time = np.zeros(self.n)
        self.distance = np.zeros(self.n)
        self.currentIndex = 0

    def setupPlot(self):
        """ Sets up plot parameters."""
        self.plotItem.setLabel("left", text="Distance", units="count")
        self.plotItem.setLabel("bottom", text="time", units="s")

    def plot(self):
        """ Plots data to the plotItem."""
        self.plotItem.plot(self.time, self.distance, clear=True)

    def uptadeData(self, newTime, newDistance):
        """ Updates time and distance data"""
        if self.currentIndex < self.n:
            self.distance[self.currentIndex] = newDistance
            self.time[self.currentIndex] = newTime
            self.distance[self.currentIndex:] = newDistance
            self.time[self.currentIndex:] = newTime
            self.currentIndex += 1
        else:
            n = self.currentIndex
            self.distance[:n-1] = self.distance[1:n]
            self.time[:n-1] = self.time[1:n]
            self.distance[n-1] = newDistance
            self.time[n-1] = newTime


if __name__ == "__main__":
    # Used here in order to get ability to ctrl+c to close program
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)

    MainWindow = AppMainWindow()
    MainWindow.window.show()

    sys.exit(app.exec_())
