from gui.gui import GUI
import data.utils as utils


def main():
    '''
    Main function to run the application.
    '''
    print(utils.get_BCI_headset_port())
    

    # Create the GUI
    app = GUI()
    app.setup_gui()
    app.run()

    

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)