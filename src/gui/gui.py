import dearpygui.dearpygui as dpg
from os import path
from data.dataset_handler import DatasetHandler
from data.data_collector import DataCollector
from models.model import ModelHandler
import os
import multiprocessing as mp
import subprocess
from gui.test_window import demo_
from numpy import random
import time
import sys
import pandas as pd

class GUI:
    '''
    Class to handle the GUI of the application.
    '''
    def __init__(self) -> None:
        '''
        Constructor of the GUI class.
        '''
        # Initialize the dearpygui context
        dpg.create_context()

        # Set the viewport size
        self.viewport_width = 800
        self.viewport_height = 600

        # Set the icon path
        self.icon_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "img"), "icon.ico")

        # Initialize the dataset handler
        self.dataset_handler = DatasetHandler()

        # Initialize the model handler
        self.model_handler = ModelHandler(self.dataset_handler)
        
    def setup_gui(self) -> None:
        '''
        Setup the GUI of the application.
        '''
        # Add containers
        self.add_data_container()
        self.add_model_container()
        self.add_output_container()

        # Create the viewport
        dpg.create_viewport(title="Super Mega Mind Reader 3000",
                            width=self.viewport_width,
                            height=self.viewport_height,
                            small_icon=self.icon_path,
                            large_icon=self.icon_path)
    
    def setup_subject_gui(self, args) -> None:
        '''
        Setup the GUI of the application for the subject.
        '''
        # Add experiment container
        self.add_experiment_container(args)

        # Create the viewport
        dpg.create_viewport(title="Super Mega Mind Reader 3000 (Experiment Mode)",
                            width=self.viewport_width,
                            height=self.viewport_height,
                            small_icon=self.icon_path,
                            large_icon=self.icon_path)

    def add_data_container(self):
        '''
        Add the data container to the GUI.
        '''
        def collect_data_cb(sender: str, app_data: dict)->None:
            '''
            Callback function for the collect data button in the data container.

            args:
                sender (str): The sender of the callback.
                app_data (dict): The data passed to the callback.

            returns:
                None

            raises:
                None
            ''' 
            # Get the classes from the input text
            class_input_text = dpg.get_value("class_input_text")
            # Remove spaces
            class_list = class_input_text.replace(" ", "")
            # Remove empty lines
            class_list = class_list.split("\n")
            # Remove empty strings
            class_list = [class_ for class_ in class_list if class_]
            # Remove duplicates
            class_list = list(set(class_list))

            # Get the cue period from the input text
            cue_period = dpg.get_value("cue_period_input_text")

            # Connect to the BCI headset if available
            print("Connecting to BCI headset...")
            dc = DataCollector()
            if not dc.port or not dc.board:
                print("BCI headset not found. Please check the connection.")
                return
            dc.print_device_info()

            print("\nStarting data collection...")

            # Start streaming data if the headset is connected
            try:
                dc.start_streaming()
            except:
                print("Failed to start streaming. Please check the headset connection.")
                return

            # Create a queue to communicate with the subject GUI
            queue = mp.Queue()
            
            # Run the script in a separate process
            print(f"pre: {class_list} {cue_period}")
            subject_gui_process = mp.Process(target=self.run_subject_gui, args=(queue, class_list, cue_period))

            # Start the subject GUI process
            subject_gui_process.start()

            # Collect data until the experiment is done
            experiment_done = False
            while not experiment_done:
                # Get the current data from the board (last 254 packages)
                channel_data = dc.get_current_board_data()
                try:
                    # Update the plots with the new data
                    for ch in range(1,9):
                        dpg.set_value(f"channel_{ch}_plot", list(channel_data[ch]))
                    
                    # Check if the experiment is done
                    experiment_done = queue.get_nowait()
                except:
                    pass
                
            # Get run dataset
            dataset = dc.get_board_data()

            # Stop streaming data
            print("\nStopping data collection...")
            dc.stop_streaming()

            # Get the path to the class timestamps file
            class_df_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'class_timestamps.csv')
            # Load the class timestamps file
            class_df = pd.read_csv(class_df_path, on_bad_lines='warn')

            # Drop unnecessary columns from the sensor dataset
            dataset = dataset.iloc[:, list(range(1, 9)) + [-2]]
            # Add headers
            dataset.columns = [f'Channel {n}' for n in range(1, 9)] + ['Timestamp']

            # Merge the sensor data dataset with the class timestamps
            merged_df = pd.merge_asof(dataset, class_df, on='Timestamp', direction='nearest')
            # Drop the rows with Class = Instructions
            merged_df = merged_df[merged_df['Class'] != 'Instructions']
            
            # Save the dataset to a CSV file
            merged_df.to_csv("merged_dataset.csv", index=False)
            
            # Wait for the subject GUI process to finish
            subject_gui_process.join()


        def file_dialog_cb(sender: str, app_data: dict)->None:
            '''
            Callback function for the file dialog in the data container.

            This function updates the dataset path and name when a file is selected, and updates the current dataset name displayed on the data container.

            args:
                sender (str): The sender of the callback.
                app_data (dict): The data passed to the callback.

            returns:
                None

            raises:
                None
            '''
            # Update the dataset path
            self.dataset_handler.raw_dataset_path = app_data['file_path_name']

            # Load the dataset
            #self.dataset_handler.load_from_csv(self.dataset_handler.raw_dataset_path)

            # Update the current dataset name displayed on the data container
            dpg.set_value("current_raw_dataset_name", f"Raw Dataset: {path.basename(self.dataset_handler.raw_dataset_path)}")
        
        def folder_dialog_cb(sender: str, app_data: dict)->None:
            '''
            Callback function for the folder dialog in the data container.

            This function updates the dataset path and name when a file is selected, and updates the current dataset name displayed on the data container.

            args:
                sender (str): The sender of the callback.
                app_data (dict): The data passed to the callback.

            returns:
                None

            raises:
                ValueError: If an invalid dataset type is loaded.
            '''
            # Update the respective dataset path and name displayed on the data container's info tab
            if dpg.get_value("load_data_combo_box") == "Train":
                self.dataset_handler.train_dataset_path = app_data['file_path_name']
                dpg.set_value("current_train_dataset_name", f"Train Dataset: {path.basename(self.dataset_handler.train_dataset_path)}")

            elif dpg.get_value("load_data_combo_box") == "Test":
                self.dataset_handler.test_dataset_path = app_data['file_path_name']
                dpg.set_value("current_test_dataset_name", f"Test Dataset: {path.basename(self.dataset_handler.test_dataset_path)}")
                
            elif dpg.get_value("load_data_combo_box") == "Valid":
                self.dataset_handler.validation_dataset_path = app_data['file_path_name']
                dpg.set_value("current_validation_dataset_name", f"Validation Dataset: {path.basename(self.dataset_handler.validation_dataset_path)}")

            else:
                raise ValueError("Invalid dataset type loaded")

        def load_data_cb(sender: str, app_data: dict)->None:
            '''
            Callback function for the load data button in the data container.
            This function shows the respective file dialog based on the selected dataset type.

            args:
                sender (str): The sender of the callback.
                app_data (dict): The data passed to the callback.

            returns:
                None

            raises:
                ValueError: If an invalid dataset type is selected.
            '''
            # Show the respective file dialog based on the selected dataset type
            dataset_type = dpg.get_value("load_data_combo_box")
            if dataset_type == "Raw":
                dpg.show_item("load_data_file_dialog")
            elif dpg.get_value("load_data_combo_box") == "Train" or dpg.get_value("load_data_combo_box") == "Test" or dpg.get_value("load_data_combo_box") == "Valid":
                dpg.show_item("load_data_folder_dialog")
            else:
                raise ValueError("Invalid dataset type selected")
            

        def preprocess_preset_cb(sender: str, app_data: dict)->None:
            '''
            Callback function for the preprocess button in the data container.
            This function preprocesses the dataset using the selected preset.

            args:
                sender (str): The sender of the callback.
                app_data (dict): The data passed to the callback.

            returns:
                None

            raises:
                ValueError: If an invalid preset is selected.
            '''
            # Get the selected preset
            preset = dpg.get_value("preprocess_preset_option")
            if preset == "O'Neill":
                # Get current timestamp
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                print("Preprocessing dataset using O'Neill's method...")
                # Load the dataset as a dataframe
                df = self.dataset_handler.load_csv_as_dataframe(self.dataset_handler.raw_dataset_path)

                # Create a folder to store the processed dataset
                store_folder_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed", f"oneill_{timestamp}")
                print("store_folder_path: ", store_folder_path)
                os.makedirs(store_folder_path, exist_ok=True)
                
                # Preprocess the dataset using O'Neill's method
                self.dataset_handler.preprocess_oneill(df,
                                                       window_size=64,
                                                       overlap=0.25,
                                                       store_folder=store_folder_path,
                                                       normalize=True)

            elif preset == "Preset A":
                print("Preprocessing dataset using Preset A...")
            elif preset == "Preset B":
                print("Preprocessing dataset using Preset B...")
            else:
                raise ValueError("Invalid preset selected")

        def load_data_combo_cb(sender: str, app_data: dict)->None:
            print("Combo box selected: ", app_data)
            # Get the current combo box value
            combo_box_value = dpg.get_value("load_data_combo_box")
            print("Combo box value: ", combo_box_value)

        with dpg.file_dialog(directory_selector=False, show=False, callback=file_dialog_cb, tag="load_data_file_dialog", width=700 ,height=400):
            dpg.add_file_extension("", color=(150, 150, 255, 255))
            dpg.add_file_extension(".csv", color=(150, 255, 150, 255))

        with dpg.file_dialog(directory_selector=True, show=False, callback=folder_dialog_cb, tag="load_data_folder_dialog", width=700 ,height=400):
            dpg.add_file_extension("", color=(150, 150, 255, 255))

        with dpg.window(label="Data",
                        width=self.viewport_width//3,
                        height=self.viewport_height//2,
                        no_close=True,
                        no_move=True,
                        no_resize=True,
                        no_background=False):
            
            def _log(sender, app_data):
                pass


            with dpg.collapsing_header(label="Collect"):
                default_classes = ["Move", "Relax"]
                default_class_list = "\n".join(default_classes)
                dpg.add_button(label="Collect", callback=collect_data_cb, tag="collect_data_button")
                dpg.add_text("Class list:")
                dpg.add_input_text(default_value=default_class_list,
                                   multiline=True,
                                   height=80,
                                   no_spaces=True,
                                   tab_input=True,
                                   tag="class_input_text")
                dpg.add_text("Cue period:")
                dpg.add_input_text(label="Seconds",
                                   decimal=True,
                                   tag="cue_period_input_text")


            with dpg.collapsing_header(label="Load"):
                dpg.add_button(label="Load", callback=load_data_cb, tag="load_data_button")
                dpg.add_combo(("Raw", "Train", "Test", "Valid"), default_value=None, tag="load_data_combo_box", callback=load_data_combo_cb)

                #with dpg.group(horizontal=True):
                 #   dpg.add_radio_button(("Raw", "Train", "Test", "Valid"), horizontal=True, default_value="Raw", tag="load_radio_button",)
            
            with dpg.collapsing_header(label="Preprocess"):
                
                with dpg.tab_bar():
                            with dpg.tab(label="Preset"):
                                dpg.add_button(label="Preprocess", callback=preprocess_preset_cb, tag="preprocess_preset_button")
                                dpg.add_text("This is the preset tab!")
                                dpg.add_radio_button(("O'Neill", "Preset A", "Preset B"), tag="preprocess_preset_option", default_value="O'Neill")
                            
                            with dpg.tab(label="Custom"):
                                dpg.add_button(label="Preprocess", callback=_log, tag="preprocess_custom_button")
                                dpg.add_text("This is the custom tab!")

                                with dpg.group(horizontal=True):
                                    dpg.add_checkbox(label="A", callback=_log, default_value=True)
                                    dpg.add_checkbox(label="B", callback=_log, default_value=True)
                                    dpg.add_checkbox(label="C", callback=_log, default_value=True)
                                    dpg.add_checkbox(label="D", callback=_log, default_value=True)
                            
            
            
            with dpg.collapsing_header(label="Info", default_open=True):
                raw_dataset_name = path.basename(self.dataset_handler.raw_dataset_path) if self.dataset_handler.raw_dataset_path else None
                train_dataset_name = path.basename(self.dataset_handler.train_dataset_path) if self.dataset_handler.train_dataset_path else None
                test_dataset_name = path.basename(self.dataset_handler.test_dataset_path) if self.dataset_handler.test_dataset_path else None
                validation_dataset_name = path.basename(self.dataset_handler.validation_dataset_path) if self.dataset_handler.validation_dataset_path else None

                dpg.add_text(f"Raw Dataset: {raw_dataset_name}", label="raw_dataset_text", wrap=self.viewport_width//4, tag="current_raw_dataset_name")
                dpg.add_text(f"Train Dataset: {train_dataset_name}", label="train_dataset_text", wrap=self.viewport_width//4, tag="current_train_dataset_name")
                dpg.add_text(f"Test Dataset: {test_dataset_name}", label="test_dataset_text", wrap=self.viewport_width//4, tag="current_test_dataset_name")
                dpg.add_text(f"Validation Dataset: {validation_dataset_name}", label="validation_dataset_text", wrap=self.viewport_width//4, tag="current_validation_dataset_name")



    def add_model_container(self):
        '''
        Add the model container to the GUI.
        '''
        def model_file_dialog_cb(sender, app_data):
            model_path = app_data['file_path_name']
            self.model_handler.load_h5_or_hdf5(model_path)
            print("Loaded Model Path: ", model_path)

        def summarize_model_cb():
            print("Model Summary")
            self.model_handler.model.summary()

        def train_model_cb():
            # Load train, test, and validation datasets
            print("Loading train, test, and validation datasets...")
            self.dataset_handler.load_train_test_val_directories()

            # Get the class weights (optional)
            print("Getting class weights...")
            class_weight_dict = self.model_handler.get_class_weights(self.dataset_handler.train_labels)

            # Train the model
            print("Training model...")
            self.model_handler.train_model(self.dataset_handler.train_images,
                                           self.dataset_handler.train_labels,
                                           self.dataset_handler.val_images,
                                           self.dataset_handler.val_labels,
                                           epochs=10,
                                           batch_size=32,
                                           class_weight_dict=class_weight_dict
                                           )
            
            # Save the model
            self.model_handler.save_model()

            # Test the model
            self.model_handler.test_model(self.dataset_handler.test_images, self.dataset_handler.test_labels)
            

        def test_model_cb():
            self.model_handler.test_model(self.dataset_handler.test_images, self.dataset_handler.test_labels)

        def test_option_cb():
            test_option = dpg.get_value("test_option_radio_button")
            print(f"'{test_option}' testing option selected")

        with dpg.file_dialog(directory_selector=False, show=False, callback=model_file_dialog_cb, tag="model_file_dialog_tag", width=700 ,height=400):
            dpg.add_file_extension("", color=(150, 150, 255, 255))
            dpg.add_file_extension(".hdf5", color=(255, 127, 80, 255))
            dpg.add_file_extension(".h5", color=(255, 127, 80, 255))

        with dpg.window(label="Model",
                        width=self.viewport_width//3,
                        height=self.viewport_height//2,
                        pos=(0, self.viewport_height//2),
                        no_close=True,
                        no_move=True,
                        no_resize=True,
                        no_background=False):
            dpg.add_button(label="Load", callback=lambda: dpg.show_item("model_file_dialog_tag"))
            dpg.add_button(label="Model Summary", callback=summarize_model_cb)
            dpg.add_button(label="Train", callback=train_model_cb)
            dpg.add_button(label="Test", callback=test_model_cb)
            dpg.add_radio_button(("Live", "From Dataset"), callback=test_option_cb, horizontal=True, default_value=0, tag="test_option_radio_button")
            
    def add_output_container(self):
        '''
        Add the output container to the GUI.
        '''
        with dpg.window(label="Output",
                        width=self.viewport_width*2//3,
                        height=self.viewport_height,
                        pos=(self.viewport_width//3, 0),
                        no_close=True,
                        no_move=True,
                        no_resize=True,
                        no_background=False,
                        tag="output_window"):
            dpg.add_text("Output goes here", label="output_text")
            
            for i in range(1, 9, 2):
                with dpg.group(horizontal=True):
                    dpg.add_text((f"Channel {i}"), tag=f"channel_{i}_text")
                    dpg.add_text((f"Channel {i+1}"), tag=f"channel_{i+1}_text", indent=self.viewport_width//3-30)
                with dpg.group(horizontal=True):
                    dpg.add_simple_plot(default_value=[0,0],
                                        tag=f"channel_{i}_plot",
                                        width=self.viewport_width//3-40,
                                        height=self.viewport_height//12,
                                        )
                    
                    dpg.add_simple_plot(default_value=[0,0],
                                        tag=f"channel_{i+1}_plot",
                                        width=self.viewport_width//3-40,
                                        height=self.viewport_height//12,
                                        )

    def add_experiment_container(self, args):
        '''
        Add the experiment container to the GUI.
        '''
        def cue_button_cb(sender, app_data):
            # Disable the button to avoid re-triggering the callback
            dpg.configure_item(sender, enabled=False)

            # Initialize the dataframe that holds the current class and the timestamp
            class_df = pd.DataFrame(columns=["Class", "Timestamp"])

            # Store the timestamp after the instructions are done
            # This will come handy later to remove any readings that were taken before the cues
            class_df.loc[len(class_df.index)] = ["Instructions", time.time()]

            print("Starting data collection...")
            print(args)
            classes = args.classes
            if not classes:
                classes = ["Move", "Relax"]
            else:
                classes = classes[0]
            print("classes @ cue_button_cb: ", classes)

            start_time = time.time()
            for class_ in classes:
                # Add the class and the timestamp in unix time to the dataframe
                class_df.loc[len(class_df.index)] = [class_, time.time()]
                print(f"Perform action for class {class_}")
                # Set cue button text to class name
                dpg.set_item_label(sender, class_)
                # Wait for cue period
                start_time = time.time()
                current_time = time.time()
                while current_time - start_time < args.cue_period:
                    current_time = time.time()

            # Save the dataframe to a csv file
            class_df.to_csv(f"class_timestamps.csv", index=False)
            # Finish the program
            sys.exit()


        with dpg.window(label="Experiment",
                        width=self.viewport_width,
                        height=self.viewport_height,
                        no_close=True,
                        no_move=True,
                        no_background=True,
                        no_scrollbar=True,
                        no_title_bar=True,
                        autosize=True,
                        tag="experiment_window",
                        user_data=args
                        ):
            instructions = '''
                                Welcome!

In this experiment, you will be asked to perform different actions at specific cues.

                          ... bla bla bla ...'''

            dpg.add_button(label=instructions,
                           width=self.viewport_width-20,
                           height=self.viewport_height-20,
                           tag="cue_button",
                           callback=cue_button_cb)

    def run(self):
        '''
        Run the GUI of the application.
        '''
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def run_subject_gui(self, queue, class_list=None, cue_period=None):
        '''
        Run the GUI of the application for the subject.
        '''
        # Set the class list and cue period to default values if not provided
        if not class_list:
            class_list = ["Move", "Relax"]
        if not cue_period:
            cue_period = 5.0
        
        # Set the command to run the script
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "subject_gui.py")
        formatted_class_list = " ".join(class_list)
        flags = '-u'
        command = f"python {flags} {script_path} --classes {formatted_class_list} --cue-period={cue_period}"
        
        # Run the script
        subprocess.run(command, shell=True)

        # Signal that the experiment has stopped
        queue.put(True)  
    