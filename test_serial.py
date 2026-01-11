import serial
import time
import binascii
from crcmod import crcmod

# Serial port configuration - modify according to actual device
PORT = 'COM6'          # Serial port (Windows: 'COM3', Linux: '/dev/ttyUSB0')
BAUDRATE = 115200        # Baud rate (common values: 9600, 19200, 38400, 57600, 115200)
PARITY = serial.PARITY_NONE
STOPBITS = serial.STOPBITS_ONE
BYTESIZE = serial.EIGHTBITS
TIMEOUT = 0.5          # Read timeout in seconds

# Create Modbus CRC16 function
modbus_crc = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)

# Command definitions (without CRC)
commands_without_crc = [
    "010600000000",  # Set drive control mode to position mode C00.00=0
    "010611010000",  # Set position profile command to absolute positioning C11.01=0
    "010603000002",  # Set position command source to step increment C03.00=2
    "0106030D0064",  # Set running speed to 100 rpm C03.0D=1
    "0106030C1388",  # Set displacement to 5000 pulses C03.0C=5000
    "010604110001",  # Enable motor and start operation C04.11=1
    "010604110000"  # Emergency stop command, disable motor C04.11=0
]

# Command descriptions
descriptions = [
    "Set drive control mode to position mode (C00.00=0)",
    "Set position profile to absolute positioning (C11.01=0)",
    "Set position command source to step increment (C03.00=2)",
    "Set running speed to 1 rpm (C03.0D=1)",
    "Set displacement to 5000 pulses (C03.0C=5000)",
    "Enable motor and start operation (C04.11=1)",
    "Emergency stop command, disable motor (C04.11=0)",
]

def calculate_crc(hex_str):
    """Calculate Modbus CRC16 for hex string"""
    data = binascii.unhexlify(hex_str)
    crc = modbus_crc(data)
    # Return CRC in little-endian format (low byte first)
    return bytes([crc & 0xFF, (crc >> 8)  & 0xFF])

def format_hex(data):
    """Format byte data to hex string"""
    return ' '.join([f"{b:02X}" for b in data])

def send_modbus_command(ser, hex_cmd, description):
    """Send single Modbus command and handle response"""
    try:
        # Calculate CRC and append to command
        crc_bytes = calculate_crc(hex_cmd)
        full_cmd = binascii.unhexlify(hex_cmd) + crc_bytes
        
        # Send command
        ser.write(full_cmd)
        print(f"\nSending command: {description}")
        print(f"Data: {format_hex(full_cmd)}")
        
        # Wait for device processing
        time.sleep(0.3)
        
        # Read response (Modbus RTU response typically 8 bytes)
        response = ser.read(8)         
        if response:
            print(f"Device response: {format_hex(response)}")
            return True
        else:
            print("Error: No response received!")
            return False
            
    except Exception as e:
        print(f"Error sending command: {str(e)}")
        return False

def main():
    # Create serial connection
    try:
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUDRATE,
            parity=PARITY,
            stopbits=STOPBITS,
            bytesize=BYTESIZE,
            timeout=TIMEOUT
        )
        print(f"Successfully connected to serial port: {ser.name}\n")
    except serial.SerialException as e:
        print(f"Failed to open serial port: {str(e)}")
        return
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return

    # Send all commands
    for i, (cmd, desc) in enumerate(zip(commands_without_crc, descriptions), 1):
        print(f"Executing command {i}/{len(commands_without_crc)}")
        success = send_modbus_command(ser, cmd, desc)
        
        if not success:
            print("Command execution failed, terminating program")
            break
            
        # Special delay for critical commands
        if "Enable" in desc or "Trigger" in desc or "Emergency" in desc:
            time.sleep(1.0)  # Longer delay for motion-related commands
        else:
            time.sleep(0.5)  # Standard delay for configuration commands
    
    # Close serial port
    ser.close()
    print("\nAll commands processed, serial port closed")

if __name__ == "__main__":
    main()