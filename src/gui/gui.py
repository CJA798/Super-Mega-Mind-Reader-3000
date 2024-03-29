import dearpygui.dearpygui as dpg

class GUI:
    def __init__(self):
        # Initialize the dearpygui context
        dpg.create_context()
        #dpg.show_style_editor()

        self.viewport_width = 800
        self.viewport_height = 600

        self.dataset_path = None
        
    def setup_gui(self):
        self.add_data_container()
        self.add_model_container()
        self.add_output_container()
        dpg.create_viewport(title="Super Mega Mind Reader 3000", width=self.viewport_width, height=self.viewport_height)

    def add_data_container(self):
        def callback(sender, app_data):
            #print("Sender: ", sender)
            #print("App Data: ", app_data)
            self.dataset_path = app_data['file_path_name']
        def preprocess_data_cb():
            pass
        with dpg.file_dialog(directory_selector=False, show=False, callback=callback, tag="file_dialog_tag", width=700 ,height=400):
            #dpg.add_file_extension(".*")
            dpg.add_file_extension("", color=(150, 150, 255, 255))
            dpg.add_file_extension(".csv", color=(150, 255, 150, 255))

        with dpg.window(label="Data",
                        width=self.viewport_width//3,
                        height=self.viewport_height//2,
                        no_close=True,
                        no_move=True,
                        no_resize=True):
            dpg.add_button(label="Load Data", callback=lambda: dpg.show_item("file_dialog_tag"))
            dpg.add_button(label="Preprocess Data", callback=preprocess_data_cb)

    def add_model_container(self):
        with dpg.window(label="Model",
                        width=self.viewport_width//3,
                        height=self.viewport_height//2,
                        pos=(0, self.viewport_height//2),
                        no_close=True,
                        no_move=True,
                        no_resize=True):
            dpg.add_text("Model goes here")

    def add_output_container(self):
        with dpg.window(label="Output",
                        width=self.viewport_width*2//3,
                        height=self.viewport_height,
                        pos=(self.viewport_width//3, 0),
                        no_close=True,
                        no_move=True,
                        no_resize=True):
            dpg.add_text("Output goes here")
    
    def run(self):
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
