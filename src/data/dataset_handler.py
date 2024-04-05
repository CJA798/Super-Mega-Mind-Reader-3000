import os
from logging import getLogger, basicConfig, INFO, info, warning, error, critical, Formatter
from pandas import read_csv
from datetime import datetime



class DatasetHandler():
    def __init__(self) -> None:
        # Initialize the logger
        self.logger = getLogger(__name__)
        self.log_directory_path = os.path.join(os.path.dirname(__file__), 'logs')
        basicConfig(filename=os.path.join(self.log_directory_path, f"dataset_handler_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"), level=INFO)

        # Initialize the dataset paths
        self.raw_dataset_path = None
        self.train_dataset_path = None
        self.validation_dataset_path = None
        self.test_dataset_path = None

        # Initialize the datasets
        self.raw_dataset = None
        self.train_dataset = None
        self.validation_dataset = None
        self.test_dataset = None

    def load_from_csv(self, file_path: str)->None:
        '''
        Load a dataset from a CSV file.

        args:
            file_path (str): The path to the CSV file.

        returns:
            None

        raises:
            ValueError: If the file path is invalid.
        '''
        try:
            # Load the dataset
            self.raw_dataset = read_csv(file_path)
            print(self.raw_dataset)
        except Exception as e:
            raise ValueError(f"An error occurred while loading the dataset: {e}")