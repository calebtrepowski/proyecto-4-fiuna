import os
from PyQt6 import QtWidgets, QtSerialPort, QtCore
from ui_generated import Ui_MainWindow

os.chdir(os.path.dirname(__file__))


class SerialTerminal:
    app: QtWidgets.QApplication
    MainWindow: QtWidgets.QMainWindow
    ui: Ui_MainWindow

    serialPort: QtSerialPort.QSerialPort

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
        self.inicializarUI()

        self.serialPort = None

    def inicializarUI(self) -> None:
        self.app = QtWidgets.QApplication([])
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        self.ui.connectButton.clicked.connect(self.manejarConexionPuerto)

        self.ui.sendDataButton.clicked.connect(self.enviarDatos)
        self.ui.dataToSendTextEdit.textChanged.connect(
            self.verificarDatosParaEnviar)

        self.ui.sendDataButton.setDisabled(True)
        self.ui.dataToSendTextEdit.setDisabled(True)

        self.ui.updateReceivedDataButton.setDisabled(True)
        self.ui.updateReceivedDataButton.clicked.connect(self.recibirDatos)

        self.ui.receivedDataText.keyPressEvent = lambda e: None

        self.rellenarOpciones()

    def verificarDatosParaEnviar(self) -> None:
        if len(self.ui.dataToSendTextEdit.toPlainText()) == 0:
            self.ui.sendDataButton.setDisabled(True)
            return

        self.ui.sendDataButton.setDisabled(False)

    def rellenarOpciones(self) -> None:
        self.ui.COMPortComboBox.addItems(
            [serialPort.portName()
             for serialPort in QtSerialPort.QSerialPortInfo().availablePorts()]
        )

        self.ui.baudRateComboBox.addItems(
            [str(baudRate) for baudRate in SerialTerminal.BAUD_RATES])
        self.ui.baudRateComboBox.setCurrentIndex(3)

    def ejecutar(self) -> int:
        self.MainWindow.show()
        return self.app.exec()

    def _conectarPuerto(self) -> bool:
        info = QtSerialPort.QSerialPortInfo(
            self.ui.COMPortComboBox.currentText())
        serialPort = QtSerialPort.QSerialPort()
        serialPort.setPort(info)
        serialPort.setBaudRate(
            SerialTerminal.BAUD_RATES[self.ui.baudRateComboBox.currentIndex()])
        serialPort.setDataBits(QtSerialPort.QSerialPort.DataBits.Data8)
        serialPort.setParity(QtSerialPort.QSerialPort.Parity.NoParity)
        serialPort.setStopBits(QtSerialPort.QSerialPort.StopBits.OneStop)

        if serialPort.open(QtCore.QIODeviceBase.OpenModeFlag.ReadWrite):
            self.serialPort = serialPort
            self.ui.COMPortComboBox.setDisabled(True)
            self.ui.baudRateComboBox.setDisabled(True)
            self.ui.connectButton.setText("Desconectar")
            self.ui.dataToSendTextEdit.setDisabled(False)
            self.ui.updateReceivedDataButton.setDisabled(False)
            return True

        return False

    def _desconectarPuerto(self) -> None:
        self.serialPort.close()
        self.serialPort = None
        self.ui.COMPortComboBox.setDisabled(False)
        self.ui.baudRateComboBox.setDisabled(False)
        self.ui.connectButton.setText("Conectar")
        self.ui.sendDataButton.setDisabled(True)
        self.ui.dataToSendTextEdit.clear()
        self.ui.dataToSendTextEdit.setDisabled(True)
        self.ui.updateReceivedDataButton.setDisabled(True)

    def manejarConexionPuerto(self) -> None:
        if self.serialPort is not None:
            self._desconectarPuerto()
            return

        self._conectarPuerto()

    def enviarDatos(self) -> None:
        self.serialPort.write(b"\n" +
                              self.ui.dataToSendTextEdit.toPlainText().encode())

    def recibirDatos(self) -> None:
        while self.serialPort.bytesAvailable() > 0:
            data = self.serialPort.read(1)
            if data == b"\r":
                self.serialPort.read(1)
                textoAnterior = self.ui.receivedDataText.toPlainText()
            else:
                textoAnterior = self.ui.receivedDataText.toPlainText()
            self.ui.receivedDataText.setPlainText(textoAnterior+data.decode())


if __name__ == "__main__":
    import sys
    serialTerminal = SerialTerminal()
    sys.exit(serialTerminal.ejecutar())
