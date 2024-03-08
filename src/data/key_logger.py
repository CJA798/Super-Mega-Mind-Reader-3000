from typing import Iterable
from pynput import keyboard
from datetime import datetime
from os import path
from csv import writer

def keylogger() -> None:
    '''
    Function to start a keylogger and save the data to a CSV file.
    The keylogger listens for key press events and saves the class and timestamp of each event.
    The class is determined by the following mapping:
    - 'i' -> Instructions
    - 'n' -> Nothing
    - 'c' -> Cue
    - 'm' -> Move
    The keylogger stops when the 'q' key is pressed.

    Args:
        - None
    Returns:
        - None

    Raises:
        - None
    '''
    # Start timestamp
    start_time = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    # Dictionary mapping keys to their corresponding class
    key_mapping = {
        'i': 'Instructions',
        'n': 'Nothing',
        'c': 'Cue',
        'm': 'Move'
    }

    # List to store the data
    data = []

    # Callback function to handle key press events
    def on_press(key: keyboard.Key) -> None:
        try:
            # Convert the key to a string
            key = key.char
            # Check if the key is in the mapping
            if key == 'q':
                # If 'q' is pressed, stop the listener and export the data to CSV
                listener.stop()
                export_data_to_csv(data)
            elif key in key_mapping:
                # Append the class and timestamp to the data list
                data.append((key_mapping[key], datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")))
        except AttributeError:
            # Ignore non-character keys
            pass

    # Function to export data to CSV file
    def export_data_to_csv(data: Iterable[Iterable[str]]) -> None:
        '''
        Function to export the data to a CSV file.
        
        Args:
            - data: List of tuples containing the class and timestamp of each key press event
        
        Returns:
            - None

        Raises:
            - None
        '''
        # Create the directory and file path
        script_dir = path.dirname(path.abspath(__file__))
        project_dir = path.dirname(path.dirname(script_dir))
        data_dir = path.join(project_dir, 'data')
        raw_data_dir = path.join(data_dir, 'raw')

        file_name = f"KEYLOGGER_{start_time}.csv"
        file_path = path.join(raw_data_dir, file_name)

        # Write the data to the CSV file
        with open(file_path, 'w', newline='') as file:
            writer_ = writer(file)
            writer_.writerow(['Class', 'Timestamp'])
            writer_.writerows(data)

    # Start the keyboard listener
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    # Print a message when the program finishes
    print("Keylogger finished.")

if __name__ == "__main__":
    print("Starting keylogger...")
    keylogger()
