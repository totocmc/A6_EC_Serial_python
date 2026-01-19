import serial
import time
import binascii
from crcmod import crcmod
from a6_servo_drive import A6_ServoDrive

# Serial port configuration - modify according to actual device
PORT = 'COM6'          # Serial port (Windows: 'COM3', Linux: '/dev/ttyUSB0')
BAUDRATE = 115200        # Baud rate (common values: 9600, 19200, 38400, 57600, 115200)
PARITY = serial.PARITY_NONE
STOPBITS = serial.STOPBITS_ONE
BYTESIZE = serial.EIGHTBITS
TIMEOUT = 0.5          # Read timeout in seconds

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

    drive = A6_ServoDrive(ser=ser, name="test")

    # Send all commands
    for i, (cmd, desc) in enumerate(zip(commands_without_crc, descriptions), 1):
        print(f"Executing command {i}/{len(commands_without_crc)}")
        success = drive.send_modbus_command(cmd, desc)
        
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