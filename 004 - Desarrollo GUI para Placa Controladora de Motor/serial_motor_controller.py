from ui_generated import Ui_MainWindow
from PyQt6 import QtWidgets, QtSerialPort, QtCore
import random
import os
os.chdir(os.path.dirname(__file__))


class SerialMotorController:
    app: QtWidgets.QApplication
    MainWindow: QtWidgets.QMainWindow
    ui: Ui_MainWindow

    serialPort: QtSerialPort.QSerialPort
    timer: QtCore.QTimer

    BAUD_RATES = (
        QtSerialPort.QSerialPort.BaudRate.Baud1200.value,
        QtSerialPort.QSerialPort.BaudRate.Baud2400.value,
        QtSerialPort.QSerialPort.BaudRate.Baud4800.value,
        QtSerialPort.QSerialPort.BaudRate.Baud9600.value,
        QtSerialPort.QSerialPort.BaudRate.Baud19200.value,
        QtSerialPort.QSerialPort.BaudRate.Baud38400.value,
        QtSerialPort.QSerialPort.BaudRate.Baud57600.value,
        QtSerialPort.QSerialPort.BaudRate.Baud115200.value,
    )

    def __init__(self) -> None:
        self.serialPort = None
        self.timer = None
        self.initializeUI()

    def initializeUI(self) -> None:
        self.app = QtWidgets.QApplication([])
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)

        self.ui.modeAutoRadioButton.clicked.connect(self._setModeAuto)
        self.ui.modeAutoRadioButton.click()

        self.ui.modeManualRadioButton.clicked.connect(self._setModeManual)

        self._fillCOMPortComboBox()
        self._fillBaudRateComboBox()
        self.ui.actionRefreshCOMPorts.triggered.connect(
            self._fillCOMPortComboBox)
        self.ui.connectButton.clicked.connect(self._handleCOMPortConnection)

        self.ui.simulateConnectionCheckBox.clicked.connect(
            self.simulateConnection)

        self.ui.cleanHistoryButton.clicked.connect(self._clearBusHistory)

        self.ui.setValuesButton.clicked.connect(self._sendValues)

    def run(self) -> int:
        self.MainWindow.show()
        return self.app.exec()

    def _setModeAuto(self, slot) -> None:
        self.ui.onOffCheckBox.setDisabled(True)
        self.ui.setPositionSlider.setDisabled(True)
        self.ui.setPidKSpinBox.setDisabled(True)
        self.ui.setPidISpinBox.setDisabled(True)
        self.ui.setPidDSpinBox.setDisabled(True)
        self.ui.setValuesButton.setDisabled(True)

    def _setModeManual(self, slot) -> None:
        if self.serialPort is not None or self.timer is not None:
            self.ui.onOffCheckBox.setEnabled(True)
            self.ui.setPositionSlider.setEnabled(True)
            self.ui.setPidKSpinBox.setEnabled(True)
            self.ui.setPidISpinBox.setEnabled(True)
            self.ui.setPidDSpinBox.setEnabled(True)
            self.ui.setValuesButton.setEnabled(True)

    def _fillCOMPortComboBox(self, slot=None) -> None:
        if self.serialPort is not None:
            self.ui.statusBar.showMessage("Desconectar para actualizar.", 2000)
            return

        self.ui.COMPortComboBox.clear()
        self.ui.COMPortComboBox.addItems(
            [serialPort.portName()
             for serialPort in QtSerialPort.QSerialPortInfo().availablePorts()]
        )

    def _fillBaudRateComboBox(self) -> None:
        self.ui.baudRateComboBox.addItems(
            [str(baudRate) for baudRate in SerialMotorController.BAUD_RATES])
        self.ui.baudRateComboBox.setCurrentIndex(3)

    def _connectCOMPort(self) -> bool:
        info = QtSerialPort.QSerialPortInfo(
            self.ui.COMPortComboBox.currentText())
        serialPort = QtSerialPort.QSerialPort()
        serialPort.setPort(info)
        serialPort.setBaudRate(
            SerialMotorController.BAUD_RATES[self.ui.baudRateComboBox.currentIndex()])
        serialPort.setDataBits(QtSerialPort.QSerialPort.DataBits.Data8)
        serialPort.setParity(QtSerialPort.QSerialPort.Parity.NoParity)
        serialPort.setStopBits(QtSerialPort.QSerialPort.StopBits.OneStop)

        if serialPort.open(QtCore.QIODeviceBase.OpenModeFlag.ReadWrite):
            self.serialPort = serialPort
            self.ui.COMPortComboBox.setDisabled(True)
            self.ui.baudRateComboBox.setDisabled(True)
            self.ui.simulateConnectionCheckBox.setDisabled(True)
            self.ui.connectButton.setText("Desconectar")
            self.ui.statusBar.showMessage("Conexión Exitosa!", 1000)

            self.serialPort.thread()
            return True

        self.ui.statusBar.showMessage("Se produjo un error al conectar.", 1000)
        self._fillCOMPortComboBox()
        return False

    def _disconnectCOMPort(self) -> None:
        self.serialPort.close()
        self.serialPort = None
        self.ui.COMPortComboBox.setDisabled(False)
        self.ui.baudRateComboBox.setDisabled(False)
        self.ui.simulateConnectionCheckBox.setDisabled(False)
        self.ui.connectButton.setText("Conectar")

    def _handleCOMPortConnection(self) -> None:
        if self.serialPort is not None:
            self._disconnectCOMPort()
            return

        self._connectCOMPort()

    def simulateConnection(self, slot=None) -> None:
        if self.timer is not None:
            self.timer.stop()
            self.timer = None
            self._clearValues()
            self.ui.COMPortComboBox.setEnabled(True)
            self.ui.baudRateComboBox.setEnabled(True)
            self.ui.connectButton.setEnabled(True)
            self.ui.statusBar.clearMessage()
            return

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._showRandomValues)
        self.timer.start(1000)

        self.ui.COMPortComboBox.setDisabled(True)
        self.ui.baudRateComboBox.setDisabled(True)
        self.ui.connectButton.setDisabled(True)

        self.ui.statusBar.showMessage("Simulando conexión...")

    def _showRandomValues(self, slot=None) -> None:
        self.ui.speedValue.setText(str(random.randint(0, 20)))
        self.ui.positionValue.setText(str(random.randint(0, 180)))
        self.ui.currentValue.setText(str(random.randint(0, 200)))
        self.ui.voltageValue.setText(f"{random.random()*12:.2f}")

        self.ui.i2cBusTextEdit.appendPlainText(
            f"Posicion Objetivo: {random.randint(0,180)}°")

    def _clearValues(self) -> None:
        self.ui.speedValue.setText("-")
        self.ui.positionValue.setText("-")
        self.ui.currentValue.setText("-")
        self.ui.voltageValue.setText("-")

    def _clearBusHistory(self, slot=None) -> None:
        self.ui.i2cBusTextEdit.clear()

    def _sendValues(self) -> None:
        on = 1 if self.ui.onOffCheckBox.isChecked() else 0
        position = self.ui.setPositionSlider.sliderPosition()
        kp = self.ui.setPidKSpinBox.value()
        ki = self.ui.setPidISpinBox.value()
        kd = self.ui.setPidDSpinBox.value()

        command = f"ON={on};Posicion={position};Kp={kp:.2f};Ki={ki:.2f};Kd={kd:.2f}"

        self.ui.i2cBusTextEdit.appendPlainText(">" + command)



if __name__ == "__main__":
    import sys
    serialMotorController = SerialMotorController()
    sys.exit(serialMotorController.run())
