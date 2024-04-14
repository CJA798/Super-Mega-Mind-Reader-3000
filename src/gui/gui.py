import dearpygui.dearpygui as dpg
from os import path
from data.dataset_handler import DatasetHandler
from data.data_collector import DataCollector
import os
import multiprocessing as mp
import subprocess
from gui.test_window import demo_

class GUI:
    def __init__(self):
        # Initialize the dearpygui context
        dpg.create_context()
        #dpg.show_style_editor()

        self.viewport_width = 800
        self.viewport_height = 600
        self.icon_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "img"), "icon.ico")

        # Initialize the dataset handler
        self.dataset_handler = DatasetHandler()
        
    def setup_gui(self):
        self.add_data_container()
        self.add_model_container()
        self.add_output_container()
        dpg.create_viewport(title="Super Mega Mind Reader 3000",
                            width=self.viewport_width,
                            height=self.viewport_height,
                            small_icon=self.icon_path,
                            large_icon=self.icon_path)
        

    def add_data_container(self):
        def collect_data_cb(sender: str, app_data: dict)->None:
            print("Connecting to BCI headset...")
            dc = DataCollector()
            dc.print_device_info()

            print("\nStarting data collection...")
            try:
                dc.start_streaming()
            except:
                print("Failed to start streaming. Please check the headset connection.")
                return

            queue = mp.Queue()
            
            # Run the script
            p1 = mp.Process(target=demo_, args=(queue,))
            p2 = mp.Process(target=print, args=("Hello"), daemon=True)

            p1.start()
            p2.start()

            # Collect data until the experiment is done
            experiment_done = False
            while not experiment_done:
                channel_data = dc.get_current_board_data()
                try:
                    for ch in range(1,9):
                        dpg.set_value(f"channel_{ch}_plot", list(channel_data[ch]))
                    experiment_done = queue.get_nowait()
                except:
                    pass
                
            
            dataset = dc.get_board_data()
            print("\nStopping data collection...")
            dc.stop_streaming()

            p1.join()
            p2.join()


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
            self.dataset_handler.load_from_csv(self.dataset_handler.raw_dataset_path)

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
            if dpg.get_value("load_radio_button") == "Train":
                self.dataset_handler.train_dataset_path = app_data['file_path_name']
                dpg.set_value("current_train_dataset_name", f"Train Dataset: {path.basename(self.dataset_handler.train_dataset_path)}")

            elif dpg.get_value("load_radio_button") == "Test":
                self.dataset_handler.test_dataset_path = app_data['file_path_name']
                dpg.set_value("current_test_dataset_name", f"Test Dataset: {path.basename(self.dataset_handler.test_dataset_path)}")
                
            elif dpg.get_value("load_radio_button") == "Valid":
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
            if dpg.get_value("load_radio_button") == "Raw":
                dpg.show_item("load_data_file_dialog")
            elif dpg.get_value("load_radio_button") == "Train" or dpg.get_value("load_radio_button") == "Test" or dpg.get_value("load_radio_button") == "Valid":
                dpg.show_item("load_data_folder_dialog")
            else:
                raise ValueError("Invalid dataset type selected")


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
                        no_resize=True):
            
            def _log(sender, app_data):
                pass
            dpg.add_button(label="Collect", callback=collect_data_cb, tag="collect_data_button")
            with dpg.collapsing_header(label="Load"):
                dpg.add_button(label="Load", callback=load_data_cb, tag="load_data_button")
    
                with dpg.group(horizontal=True):
                    dpg.add_radio_button(("Raw", "Train", "Test", "Valid"), horizontal=True, default_value="Raw", tag="load_radio_button")
            
            with dpg.collapsing_header(label="Preprocess"):
                dpg.add_button(label="Preprocess", callback=_log)
                with dpg.tab_bar():
                            with dpg.tab(label="Preset"):
                                dpg.add_text("This is the preset tab!")
                                dpg.add_radio_button(("O'Neill", "Preset A", "Preset B"))
                            
                            with dpg.tab(label="Custom"):
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
        def callback(sender, app_data):
            self.model_path = app_data['file_path_name']
            print("Loaded Model Path: ", self.model_path)

        def train_model_cb():
            print("Training model")

        def test_model_cb():
            print("Testing model")

        def test_option_cb():
            print("Training option selected")

        with dpg.file_dialog(directory_selector=False, show=False, callback=callback, tag="model_file_dialog_tag", width=700 ,height=400):
            dpg.add_file_extension("", color=(150, 150, 255, 255))
            dpg.add_file_extension(".hdf5", color=(255, 127, 80, 255))

        with dpg.window(label="Model",
                        width=self.viewport_width//3,
                        height=self.viewport_height//2,
                        pos=(0, self.viewport_height//2),
                        no_close=True,
                        no_move=True,
                        no_resize=True):
            dpg.add_button(label="Load", callback=lambda: dpg.show_item("model_file_dialog_tag"))
            dpg.add_button(label="Train", callback=train_model_cb)
            dpg.add_button(label="Test", callback=test_model_cb)
            dpg.add_radio_button(("Live", "From Dataset"), callback=test_option_cb, horizontal=True, default_value=0)
            
    def add_output_container(self):
        with dpg.window(label="Output",
                        width=self.viewport_width*2//3,
                        height=self.viewport_height,
                        pos=(self.viewport_width//3, 0),
                        no_close=True,
                        no_move=True,
                        no_resize=True,
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

        
    def run(self):
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
