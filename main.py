import signal
import sys
import ast
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2 import QtCore
import pyqtgraph as pg
import numpy as np
from ArduinoController import ArduinoController


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
        self.window.ConnectButton.clicked.connect(self.connectArduino)
        self.window.CloseButton.clicked.connect(self.disconnectArduino)
        self.setupWidgets()
        self.distancePlot = DistancePlot(self.window.Plot.getPlotItem())
        self.threadpool = QtCore.QThreadPool()
        self.arduinoThread = None

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

    def connectArduino(self):
        """ Makes new thread in charge of communications with an
        Arduino"""
        self.distancePlot.resetArrays()
        serialPort = self.window.SerialPort.text()
        baudRate = self.window.BaudRate.value()
        self.arduinoThread = Arduino(serialPort, baudRate)
        self.arduinoThread.signals.newData.connect(self.updatePlot)
        self.threadpool.start(self.arduinoThread)

    def disconnectArduino(self):
        """ Stops connection with the arduino. """
        self.arduinoThread.close()

    def updatePlot(self, a):
        """ Adds data to the plot"""
        x = float(a[1]) / 1000
        y = float(a[0])
        self.distancePlot.uptadeData(x, y)
        self.distancePlot.plot()

    def ardTest(self):
        worker = Arduino("123", "abd")
        worker.signals.newData.connect(self.updatePlot)
        self.threadpool.start(worker)


class Arduino (QtCore.QRunnable):
    """ Worker thread"""
    def __init__(self, serialPort, baudRate, *args, **kwargs):
        super().__init__()
        self.signals = ArduinoSignals()
        self.arduino = ArduinoController(serialPort, baudRate)
        self.toClose = False

    @QtCore.Slot()
    def run(self):
        """ Initialize the runner function """
        while self.arduino.isOpen():
            a = self.arduino.read()
            if a:
                try:
                    newData = ast.literal_eval(a)
                    self.signals.newData.emit(newData)
                except SyntaxError:
                    print(a)

    def close(self):
        self.arduino.stop()


class ArduinoSignals(QtCore.QObject):
    """ Sginals available for worker thread"""
    newData = QtCore.Signal(list)


class DistancePlot():
    def __init__(self, plotItem):
        self.plotItem = plotItem
        self.setupPlot()
        self.n = 1000
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

    def resetArrays(self):
        self.time = np.zeros(self.n)
        self.distance = np.zeros(self.n)


if __name__ == "__main__":
    # Used here in order to get ability to ctrl+c to close program
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)

    MainWindow = AppMainWindow()
    MainWindow.window.show()

    sys.exit(app.exec_())
