import dearpygui.dearpygui as dpg
from gui.gui import GUI
import argparse
import sys
from typing import Iterable

# Parse command line arguments
parser = argparse.ArgumentParser(description="Run the data collection experiment.")
parser.add_argument("--classes", nargs='+', action='append', help="Classes to collect data for.")
#parser.add_argument("--skip_instructions", action="store_true", help="Skip instructions screen.")
parser.add_argument("--cue-period", type=float, default=5.0, help="Amount of time spent in each cue.")

# Parse the arguments
try:
    args = parser.parse_known_args()[0]

# If the arguments are not valid, print the help message and exit
except:
    print("")
    parser.print_help()
    sys.exit(0)

def main(args: argparse.Namespace = args) -> None:
    '''
    Main function to run the application.
    '''
    app = GUI()
    app.setup_subject_gui(args)
    app.run()
    

if __name__ == '__main__':
    main(args=args)