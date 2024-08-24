import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import os
import subprocess

'''
This script is used to test features
'''

def test_window():
    dpg.create_context()
    dpg.create_viewport(title='Custom Title', width=600, height=600)

    demo.show_demo()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

def demo_(queue):
    # Do your work here
    script_path = os.path.join(os.path.dirname(__file__), "test_window.py")
    print(script_path)
    subprocess.run(f"python {script_path}", shell=True)
    queue.put(True)  # Signal that the loop has stopped
    
            


if __name__ == '__main__':
    test_window()