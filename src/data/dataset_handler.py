import os
from logging import getLogger, basicConfig, INFO, info, warning, error, critical, Formatter
from datetime import datetime
import pandas as pd
from typing import Optional, Union, Iterable
import numpy as np      
import math
import tifffile
import time

from scipy.stats import zscore
from tqdm import tqdm


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

        # Initialize the image data
        self.train_images = None
        self.val_images = None
        self.test_images = None

        # Initialize the label data
        self.train_labels = None
        self.val_labels = None
        self.test_labels = None


    def load_csv_as_dataframe(self, file_path: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        Load a CSV file into a pandas DataFrame.

        args:
            file_path (str): Path to the CSV file.
            **kwargs: Additional keyword arguments to pass to pd.read_csv.

        returns:
            pd.DataFrame or None: The loaded DataFrame, or None if the file cannot be read.
        """
        try:
            df = pd.read_csv(file_path, **kwargs)
            return df
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return None
        except Exception as e:
            print(f"Error: Failed to load '{file_path}': {e}")
            return None
    
    def get_spatial_matrix(self, channel_readings: Iterable) -> np.array:
        """
        Create a spatial matrix from the channel readings.

        args:
            channel_readings (Iterable): The channel readings.

        returns:
            np.array: The spatial matrix.
        """
        # Get the channel values
        r = channel_readings[:-2].values

        # Create the spatial matrix
        spatial_matrix = [[0,    0,    0,    0,    r[0], 0,    r[1], 0,    0,    0,    0],
                            [0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0],
                            [0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0],
                            [0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0],
                            [0,    0,    0,    r[2], 0,    0,    0,    r[3], 0,    0,    0],
                            [0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0],
                            [0,    r[4], 0,    0,    0,    0,    0,    0,    0,    r[5], 0],
                            [0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0],
                            [0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0],
                            [0,    0,    0,    0,    r[6], 0,    r[7], 0,    0,    0,    0]]

        return np.array(spatial_matrix)
    
    def preprocess_oneill(self, df: pd.DataFrame, window_size: Union[int, float], overlap: float, store_folder: str, normalize: bool=True) -> None:
        """
        Preprocess the O'Neill dataset and store the data as TIFF images.
        
        args:
            df (pd.DataFrame): The dataset as a DataFrame.
            window_size (Union[int, float]): The size of the window.
            overlap (float): The overlap between windows.
            store_folder (str): The folder to store the TIFF images.
            
        returns:
            None
        """
        # Get names of unique classes
        classes = df['Class'].unique().tolist()

        # Process data for each class
        for _class in classes:
            # Create a dataframe containing only the data for a specific class
            class_df = df[df['Class'] == _class].copy()

            # Add a column that contains the spatial matrices
            class_df['Spatial Matrix'] = class_df.apply(self.get_spatial_matrix, axis=1)

            # Get the number of samples in the dataset
            num_samples = len(class_df)

            # Calculate the number of TIFF images to create
            #num_images = math.floor( num_samples / (window_size * overlap) ) - 1

            # Calculate the step size
            step_size = math.floor(window_size * (1-overlap))

            # Create folder if it doesn't exist
            folder_path = os.path.join(store_folder, _class)
            os.makedirs(folder_path, exist_ok=True)

            # Create and store TIFF images of the respective class
            for index, n in enumerate(tqdm(range(0, num_samples, step_size), desc=f"Processing {_class}", colour="green", unit="images")):
                # Create the image
                image = class_df['Spatial Matrix'].iloc[n: n+window_size]
                image = np.stack(image)
                # image.shape --> (window_size, 10, 11)
                # This is the numpy format for a stack of n 10x11 matrices

                # Check if the image size matches target size
                if len(image) != window_size:
                    continue

                # Normalize the image data about the depth axis
                if normalize:
                    normalized_image = zscore(image, axis=0)
                    # Replace NaN values with 0
                    np.nan_to_num(normalized_image, copy=False, nan=0.0)

                # Save TIFF image with timestamp in class folder
                file_path = os.path.join(folder_path, f"{_class}_{index}.tif")  # Adjust file name as needed
                tifffile.imwrite(file_path, normalized_image)

    def load_tiff_data(self, data_dir):
        if data_dir is None:
            raise ValueError("Data directory not set.")

        images = []
        labels = []
        class_names = os.listdir(data_dir)
        for class_name in class_names:
            class_dir = os.path.join(data_dir, class_name)
            for file_name in os.listdir(class_dir):
                file_path = os.path.join(class_dir, file_name)
                with tifffile.TiffFile(file_path) as tif:
                    image = tif.asarray()  # Load the image data
                    images.append(image)
                    labels.append(class_name)

        # Convert lists to numpy arrays
        images = np.array(images)
        labels = np.array(labels)

        # Convert class names to integer labels
        label_map = {name: i for i, name in enumerate(class_names)}
        labels = np.array([label_map[label] for label in labels])

        return images, labels
    
    def load_train_test_val_directories(self)-> None:
        self.train_images, self.train_labels = self.load_tiff_data(self.train_dataset_path)
        self.val_images, self.val_labels = self.load_tiff_data(self.validation_dataset_path)
        self.test_images, self.test_labels = self.load_tiff_data(self.test_dataset_path)