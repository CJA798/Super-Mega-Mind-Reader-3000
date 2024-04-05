from gui.gui import GUI


def main():
    '''
    Main function to run the application.
    '''
    app = GUI()
    app.setup_gui()
    app.run()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)