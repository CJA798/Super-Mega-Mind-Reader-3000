import serial.tools.list_ports
   
def get_BCI_headset_port() -> str:
    '''
    Find the port of the BCI headset.

    args:
        None

    returns:
        str: The port of the BCI headset.
    '''
    ports = serial.tools.list_ports.comports()

    for port in ports:
        if port.serial_number == 'DM0258NJA':
            return port.device
    return None