import pymodbus.client as mb

DEVICE_ADDRESS = 10
COIL_ADDRESS = 100
INPUT_REGISTER_1_ADDRESS = 104
INPUT_REGISTER_2_ADDRESS = 120
HOLDING_REGISTER_ADDRESS = 150
DEVICE_PORT = "COM1"


client = mb.ModbusSerialClient(DEVICE_PORT, baudrate=9600)
client.connect()

client.write_coil(COIL_ADDRESS, False, DEVICE_ADDRESS)
client.write_coil(COIL_ADDRESS, True, DEVICE_ADDRESS)
result = client.read_input_registers(INPUT_REGISTER_2_ADDRESS, slave=DEVICE_ADDRESS)
print(result.registers)
result = client.write_register(HOLDING_REGISTER_ADDRESS, 8, slave=DEVICE_ADDRESS)
print(result)
