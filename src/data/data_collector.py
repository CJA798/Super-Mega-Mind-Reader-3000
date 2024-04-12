import serial.tools.list_ports
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
from brainflow.data_filter import DataFilter
from time import sleep
import pandas as pd
import numpy as np

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

    def get_data(self):
        data = self.board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
        #data = self.board.get_board_data()  # get all data and remove it from internal buffer

        # demo how to convert it to pandas DF and plot data
        eeg_channels = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD.value)
        df = pd.DataFrame(np.transpose(data))
        #print('Data From the Board')
        #print(df.head(10))

        channel_data = df[eeg_channels]
        #print('Data from Channels')
        #print(channel_data.head(10))

        # demo for data serialization using brainflow API, we recommend to use it instead pandas.to_csv()
        #DataFilter.write_file(data, 'test.csv', 'w')  # use 'a' for append mode
    
        return channel_data
    
    def stop_streaming(self):
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