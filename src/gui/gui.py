import dearpygui.dearpygui as dpg
from os import path
class GUI:
    def __init__(self):
        # Initialize the dearpygui context
        dpg.create_context()
        #dpg.show_style_editor()

        self.viewport_width = 800
        self.viewport_height = 600

        self.dataset_path = None
        self.dataset_name = None
        self.model_path = None
        
    def setup_gui(self):
        self.add_data_container()
        self.add_model_container()
        self.add_output_container()
        dpg.create_viewport(title="Super Mega Mind Reader 3000",
                            width=self.viewport_width,
                            height=self.viewport_height)
        

    def add_data_container(self):
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
            self.dataset_path = app_data['file_path_name']

            # Update the dataset name
            self.dataset_name = path.basename(self.dataset_path)
            
            # Update the current dataset name displayed on the data container
            dpg.set_value("current_dataset_name", f"Current dataset: {self.dataset_name}")
        
        def preprocess_data_cb():
            print("Preprocessing data")

        def collect_data_cb():
            print("Collecting data")

        with dpg.file_dialog(directory_selector=False, show=False, callback=file_dialog_cb, tag="data_file_dialog_tag", width=700 ,height=400):
            #dpg.add_file_extension(".*")
            dpg.add_file_extension("", color=(150, 150, 255, 255))
            dpg.add_file_extension(".csv", color=(150, 255, 150, 255))

        with dpg.window(label="Data",
                        width=self.viewport_width//3,
                        height=self.viewport_height//2,
                        no_close=True,
                        no_move=True,
                        no_resize=True):
            dpg.add_button(label="Load", callback=lambda: dpg.show_item("data_file_dialog_tag"), tag="load_data_button")
            dpg.add_button(label="Preprocess", callback=preprocess_data_cb, tag="preprocess_data_button")
            dpg.add_button(label="Collect", callback=collect_data_cb, tag="collect_data_button")
            dpg.add_text(f"Current dataset: {self.dataset_name}", label="output_text", tag="current_dataset_name", wrap=self.viewport_width//4)

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
                        no_resize=True):
            dpg.add_text("Output goes here", label="output_text")
        
    def run(self):
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
