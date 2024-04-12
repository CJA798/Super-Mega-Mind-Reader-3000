import serial.tools.list_ports
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
from time import sleep
class DataCollector():
    def __init__(self):
        '''
        Constructor for the DataCollector class.
        '''
        self.port = self.get_BCI_headset_port()
        self.board = self.connect_to_BCI_headset()

    def get_BCI_headset_port(self) -> str:
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
                return port
        return None
    
    def connect_to_BCI_headset(self):
        params = BrainFlowInputParams()
        params.serial_port = self.port.device
        return BoardShim(BoardIds.CYTON_BOARD, params)
    
    def start_streaming(self):
        self.board.prepare_session()
        self.board.start_stream()
        sleep(1)
        # data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
        data = self.board.get_board_data()  # get all data and remove it from internal buffer
        self.board.stop_stream()
        self.board.release_session()
    
    def print_device_info(self):
        '''
        Print the information of the BCI headset.
        '''
        print('\nBCI HEADSET INFO:')
        print('-----------------')
        
        # Print the value of the attributes if not None
        info = self.port.__dict__
        for key, value in info.items():
            if value is not None:
                print(f"{key}: {value}")