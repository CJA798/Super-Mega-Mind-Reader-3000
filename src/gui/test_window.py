import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import os
import subprocess
def test_window():
    dpg.create_context()
    dpg.create_viewport(title='Custom Title', width=600, height=600)

    demo.show_demo()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

def demo_():
    # Path to the script you want to run
    script_path = os.path.join(os.path.dirname(__file__), "test_window.py")
    print(script_path)

    subprocess.run(f"python {script_path}", shell=True)
            


if __name__ == '__main__':
    test_window()