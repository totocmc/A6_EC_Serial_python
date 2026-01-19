import serial
import time
import binascii

class SerialModbus:

    def __init__(self, name):
        self.name = name
        # Create Modbus CRC16 function
        self.__modbus_crc = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)

    def __str__(self):
        print("Hello, my name is " + self.name)

    def __repr__(self):
        return "A6_SERVO_DRIVE(name='{}')".format(self.name)

    def calculate_crc(self, hex_str):
        """Calculate Modbus CRC16 for hex string"""
        data = binascii.unhexlify(hex_str)
        crc = self.__modbus_crc(data)
        # Return CRC in little-endian format (low byte first)
        return bytes([crc & 0xFF, (crc >> 8)  & 0xFF])

    def format_hex(self, data):
        """Format byte data to hex string"""
        return ' '.join([f"{b:02X}" for b in data])

    def send_modbus_command(self, ser, hex_cmd, description):
        """Send single Modbus command and handle response"""
        try:
            # Calculate CRC and append to command
            crc_bytes = self.calculate_crc(hex_cmd)
            full_cmd = binascii.unhexlify(hex_cmd) + crc_bytes
            
            # Send command
            ser.write(full_cmd)
            print(f"\nSending command: {description}")
            print(f"Data: {self.format_hex(full_cmd)}")
            
            # Wait for device processing
            time.sleep(0.3)
            
            # Read response (Modbus RTU response typically 8 bytes)
            response = ser.read(8)         
            if response:
                print(f"Device response: {self.format_hex(response)}")
                return True
            else:
                print("Error: No response received!")
                return False
                
        except Exception as e:
            print(f"Error sending command: {str(e)}")
            return False
