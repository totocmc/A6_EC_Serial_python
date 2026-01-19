import serial
import time
import binascii
from crcmod import crcmod
import json

class A6_ServoDrive:

    def __init__(self, ser:serial.Serial, pathToDict):
        self.__serial = ser
        # Create Modbus CRC16 function
        self.__modbus_crc = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)

        try:
            with open(pathToDict, 'r') as file:
                self.__regList = json.load(file)
                print("File data =", self.__regList)
            
        except FileNotFoundError:
            print(f"Error: The file {self.__regList} was not found.")

    def __repr__(self):
        return "A6_SERVO_DRIVE(name='{}')".format(self.__serial)
    
    def byte_from_int(self, address:int, byte_count:int):
        return address.to_bytes(byte_count, byteorder='big')

    def calculate_crc(self, hex_str:str):
        """Calculate Modbus CRC16 for hex string"""
        data = binascii.unhexlify(hex_str)
        crc = self.__modbus_crc(data)
        # Return CRC in little-endian format (low byte first)
        return bytes([crc & 0xFF, (crc >> 8)  & 0xFF])
    
    def calculate_crc(self, hex_bytes:bytes):
        """Calculate Modbus CRC16 for hex bytes"""
        crc = self.__modbus_crc(hex_bytes)
        print(crc)
        # Return CRC in little-endian format (low byte first)
        return bytes([crc & 0xFF, (crc >> 8)  & 0xFF])

    def format_hex(self, data):
        """Format byte data to hex string"""
        return ' '.join([f"{b:02X}" for b in data])

    def create_modbus_command(self, cmdName:str, value:int):
        print(self.__regList["params"][cmdName])
        cmd = bytes([0x01])
        reg = self.__regList["params"][cmdName]
        if(reg["type"] == "U16"):
            cmd = cmd + bytes([0x06])
            cmd = cmd + self.byte_from_int(reg["index"], 1)
            cmd = cmd + self.byte_from_int(reg["subIndex"], 1)
            cmd = cmd + self.byte_from_int(value, 2)
        else:
            cmd = cmd + bytes([0x03])
            cmd = cmd + self.byte_from_int(reg["index"], 1)
            cmd = cmd + self.byte_from_int(reg["subIndex"], 1)
            cmd = cmd + self.byte_from_int(value, 4)
        
        cmd = cmd + self.calculate_crc(cmd)
        print(cmd.hex(":"))
        return (cmd, reg["description"])

    def send_modbus_command(self, cmdName:str, value:int):
        """Send single Modbus command and handle response"""
        try:            
            # Send command
            (cmd,desc) = self.create_modbus_command(cmdName=cmdName, value=value)
            self.__serial.write(cmd)
            print(f"\nSending command: {desc}")
            print("Data: ", cmd.hex(":"))
            
            # Wait for device processing
            time.sleep(0.3)
            
            # Read response (Modbus RTU response typically 8 bytes)
            response = self.__serial.read(8)         
            if response:
                print(f"Device response: {self.format_hex(response)}")
                return True
            else:
                print("Error: No response received!")
                return False
                
        except Exception as e:
            print(f"Error sending command: {str(e)}")
            return False

if __name__ == "__main__":
    # Create serial connection
    try:
        ser = serial.Serial(
            port='/dev/cu.debug-console',        # Serial port (Windows: 'COM3', Linux: '/dev/ttyUSB0')
            baudrate=115200,    # Baud rate (common values: 9600, 19200, 38400, 57600, 115200)
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )
        print(f"Successfully connected to serial port: {ser.name}\n")
    except serial.SerialException as e:
        print(f"Failed to open serial port: {str(e)}")
        exit()
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        exit()
    
    drive = A6_ServoDrive(ser, "dictionary/A6_EC_Modbus.json")
    drive.send_modbus_command("C00.00", 1)