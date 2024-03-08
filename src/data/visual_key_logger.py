from typing import Iterable
from pynput import keyboard
from datetime import datetime
from os import path
from csv import writer
import tkinter as tk
import threading

def keylogger() -> None:
    '''
    Function to start a keylogger and save the data to a CSV file.
    The keylogger listens for key press events and saves the class and timestamp of each event.
    The class is determined by the following mapping:
    - 'i' -> Instructions (display blue window)
    - 'n' -> Nothing (display white window)
    - 'c' -> Cue (display green window)
    - 'm' -> Move (display yellow window)
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
    # Dictionary mapping keys to their corresponding class and text
    key_mapping = {
        'i': ('Instructions', 'yellow'),
        'n': ('Nothing', 'white'),
        'c': ('Cue', 'green'),
        'm': ('Move', 'red')
    }

    # List to store the data
    data = []

    # Create a tkinter window
    root = tk.Tk()
    root.title("Keylogger Window")
    root.geometry("200x200")

    # Create a label for displaying text
    label_text = tk.StringVar()
    label_text.set("Press any key")
    label = tk.Label(root, textvariable=label_text)
    label.pack(expand=True)

    # Global variable to store the listener
    global listener

    # Callback function to handle key press events
    def on_press(key: keyboard.Key) -> None:
        try:
            # Convert the key to a string
            key = key.char
            # Check if the key is in the mapping
            if key in key_mapping:
                # Append the class and timestamp to the data list
                data.append((key_mapping[key][0], datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")))
                # Update the label text based on the key pressed
                label_text.set(key_mapping[key][0])
                # Change the window color
                root.configure(bg=key_mapping[key][1])
        except AttributeError:
            # Ignore non-character keys
            pass

    # Function to stop the listener and export data to CSV
    def stop_and_export():
        if listener:
            listener.stop()
            export_data_to_csv(data)
            root.destroy()

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

    # Start the keyboard listener in a separate thread
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # Check for the 'q' key to stop the listener and export the data
    root.bind('<KeyPress-q>', lambda event: stop_and_export())

    # Start the tkinter main loop
    root.mainloop()

    # Print a message when the program finishes
    print("Keylogger finished.")

if __name__ == "__main__":
    print("Starting keylogger...")
    keylogger()
