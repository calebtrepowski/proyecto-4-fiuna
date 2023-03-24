import os
os.chdir(os.path.dirname(__file__))

import pymodbus.client as mb
from pymodbus.exceptions import ModbusException
import pymodbus.pdu as pdu
from PyQt6 import QtWidgets, QtSerialPort, QtCore, QtGui
from ui_generated import Ui_MainWindow


BaudRate = QtSerialPort.QSerialPort.BaudRate


class ModbusClientGUI:
    app: QtWidgets.QApplication
    MainWindow: QtWidgets.QMainWindow
    ui: Ui_MainWindow

    modbusSerialClient: mb.ModbusSerialClient
    modbusDeviceAddress: int

    BAUD_RATES = (
        BaudRate.Baud1200.value,
        BaudRate.Baud2400.value,
        BaudRate.Baud4800.value,
        BaudRate.Baud9600.value,
        BaudRate.Baud19200.value,
        BaudRate.Baud38400.value,
        BaudRate.Baud57600.value,
        BaudRate.Baud115200.value,
    )

    def __init__(self) -> None:
        self.initializeUI()

        self.modbusSerialClient = None

    def initializeUI(self) -> None:
        self.app = QtWidgets.QApplication([])
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)

        self._initializeSerialConfigurationUI()
        self._initializeWriteHoldingRegisterUI()
        self._initializeReadInputRegisterUI()
        self._initializeWriteCoilsUI()

    def _initializeSerialConfigurationUI(self) -> None:
        self._setDisableReadWriteFields(True)

        self._updateSerialPorts()

        self.ui.serialBaudrateComboBox.addItems(
            [str(baudRate) for baudRate in ModbusClientGUI.BAUD_RATES])
        self.ui.serialBaudrateComboBox.setCurrentIndex(3)

        self.ui.serialDeviceModbusAddressLineEdit.setValidator(
            QtGui.QIntValidator())

        self.ui.serialPortConnectButton.clicked.connect(
            self._handleSerialConnection)

        self.ui.actionUpdatePorts.triggered.connect(self._updateSerialPorts)

    def _initializeWriteHoldingRegisterUI(self) -> None:
        self.ui.writeRegisterButton.clicked.connect(self._writeHoldingRegister)

    def _initializeReadInputRegisterUI(self) -> None:
        self.ui.readRegisterButton.clicked.connect(self._readInputRegister)


    def _generateCoilCheckBoxHandler(self, coilCheckBox: QtWidgets.QCheckBox):
        coilNumber = int(coilCheckBox.text().split()[1])

        def writeCoil(slot) -> None:
            try:
                result = self.modbusSerialClient.write_coil(
                    coilNumber, slot, slave=self.modbusDeviceAddress)

                if not result.isError():
                    self.ui.statusbar.showMessage(
                        "Escritura realizada correctamente", 3000)
                
                elif type(result) == pdu.ExceptionResponse:
                    raise ModbusException(pdu.ModbusExceptions.decode(result.exception_code))
                else:
                    raise ModbusException("Unkown error")
            except ModbusException as me:
                coilCheckBox.setChecked(not slot)
                self.ui.statusbar.showMessage(
                    f"Se produjo un error: {me}", 5000)
                
        return writeCoil

    def _initializeWriteCoilsUI(self) -> None:
        self.coilCheckBoxeslist: list[QtWidgets.QCheckBox] = [
            self.ui.writeCoil1CheckBox,
            self.ui.writeCoil2CheckBox,
            self.ui.writeCoil3CheckBox,
            self.ui.writeCoil4CheckBox,
            self.ui.writeCoil5CheckBox,
            self.ui.writeCoil6CheckBox,
            self.ui.writeCoil7CheckBox,
            self.ui.writeCoil8CheckBox
        ]

        for coilCheckBox in self.coilCheckBoxeslist:
            coilCheckBox.clicked.connect(self._generateCoilCheckBoxHandler(coilCheckBox))

    


    def _writeHoldingRegister(self) -> None:
        try:
            registerAddress = int(
                self.ui.writeRegisterAddressLineEdit.text(), base=16)
        except ValueError:
            self.ui.statusbar.showMessage(
                "Escribir una dirección de registro válida", 5000)
            return

        try:
            writeValue = int(
                self.ui.writeRegisterValueLineEdit.text(), base=16)
        except ValueError:
            self.ui.statusbar.showMessage(
                "Escribir un valor para registro válido", 5000)
            return

        try:
            result = self.modbusSerialClient.write_register(
                registerAddress, writeValue, slave=self.modbusDeviceAddress)

            if not result.isError():
                self.ui.statusbar.showMessage(
                    "Escritura realizada correctamente", 3000)
            
            elif type(result) == pdu.ExceptionResponse:
                raise ModbusException(pdu.ModbusExceptions.decode(result.exception_code))
            else:
                raise ModbusException("Unkown error")

        except ModbusException as me:
            self.ui.statusbar.showMessage(f"Se produjo un error: {me}", 5000)

    def _readInputRegister(self) -> None:
        try:
            registerAddress = int(
                self.ui.readRegisterAddressLineEdit.text(), base=16)
        except ValueError:
            self.ui.statusbar.showMessage(
                "Escribir una dirección de registro válida", 3000)
            return

        try:
            result = self.modbusSerialClient.read_input_registers(
                registerAddress, slave=self.modbusDeviceAddress)

            if not result.isError():
                self.ui.readRegisterValueLineEdit.setText(
                    str(hex(result.registers[0]))[2:].capitalize())
                
            elif type(result) == pdu.ExceptionResponse:
                raise ModbusException(pdu.ModbusExceptions.decode(result.exception_code))
            else:
                raise ModbusException("Unkown error")

        except ModbusException as me:
            self.ui.statusbar.showMessage(f"Se produjo un error: {me}", 5000)

    def _setDisableReadWriteFields(self, disable: bool) -> None:
        writeHoldingRegistersFields: list[QtWidgets.QPushButton | QtWidgets.QLineEdit] = self.ui.writeHoldingRegistersGroupBox.findChildren(
            (QtWidgets.QPushButton, QtWidgets.QLineEdit))
        readInputRegistersFields: list[QtWidgets.QPushButton | QtWidgets.QLineEdit] = self.ui.readInputRegisterGroupBox.findChildren(
            (QtWidgets.QPushButton, QtWidgets.QLineEdit))
        writeCoilsFields: list[QtWidgets.QCheckBox] = self.ui.writeCoilsGroupBox.findChildren(
            QtWidgets.QCheckBox)

        for field in (*writeHoldingRegistersFields, *readInputRegistersFields, *writeCoilsFields):
            field.setDisabled(disable)

    def _setDisableSerialConfigurationFields(self, disable: bool) -> None:
        serialDeviceConfigurationFields: list[QtWidgets.QComboBox, QtWidgets.QLineEdit] = self.ui.serialDeviceConfigurationGroupBox.findChildren(
            (QtWidgets.QComboBox, QtWidgets.QLineEdit))

        for field in serialDeviceConfigurationFields:
            field.setDisabled(disable)

    def _updateSerialPorts(self) -> None:
        self.ui.serialPortComboBox.clear()
        self.ui.serialPortComboBox.addItems(
            [serialPort.portName()
             for serialPort in QtSerialPort.QSerialPortInfo().availablePorts()]
        )

    def _handleSerialConnection(self) -> None:
        if self.modbusSerialClient is None:
            self._connectSerialDevice()
            return

        self._disconnectSerialDevice()

    def _connectSerialDevice(self) -> None:
        serialPort = self.ui.serialPortComboBox.currentText()
        baudRate = ModbusClientGUI.BAUD_RATES[self.ui.serialBaudrateComboBox.currentIndex(
        )]
        try:
            deviceAddress = int(
                self.ui.serialDeviceModbusAddressLineEdit.text())
        except ValueError:
            self.ui.statusbar.showMessage(
                "Especificar dirección del dispositivo en el bus", 5000)
            return

        self.modbusSerialClient = mb.ModbusSerialClient(
            serialPort, baudrate=baudRate)
        self.modbusDeviceAddress = deviceAddress
        self.modbusSerialClient.deviceAddress = deviceAddress

        if self.modbusSerialClient.connect():
            self._setDisableSerialConfigurationFields(True)
            self._setDisableReadWriteFields(False)
            self.ui.serialPortConnectButton.setText("Desconectar")
        else:
            self.ui.statusbar.showMessage(
                "Se produjo un error al conectar", 5000)

    def _disconnectSerialDevice(self) -> None:
        self.modbusSerialClient.close()
        self.modbusSerialClient = None

        self._setDisableSerialConfigurationFields(False)
        self._setDisableReadWriteFields(True)
        self.ui.serialPortConnectButton.setText("Conectar")

    def run(self) -> int:
        self.MainWindow.show()
        return self.app.exec()
