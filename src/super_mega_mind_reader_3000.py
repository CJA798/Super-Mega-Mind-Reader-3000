from gui.gui import GUI
import data.utils as utils


def main():
    '''
    Main function to run the application.
    '''
    app = GUI()
    app.setup_gui()
    app.run()
    

if __name__ == '__main__':
    # Run the main function
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)