import serial.tools.list_ports
ports = serial.tools.list_ports.comports()


for port in ports:
      if port.serial_number == 'DM0258NJA':
          print(f'BCI Device found on port: {port.device}')
          break 

