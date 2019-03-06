import logging, json, sys
from interpreter import interpreter, Container, semantic

import tkinter as tk
from tkinter.filedialog import *
from tkinter.messagebox import *
from views import menuBar

def setUp_Logger(log_level):
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=log_level,
                        format='%(name)s:%(levelname)s: %(message)s')

def getLoggingLevel():
    if(sys.argv[1] in ['--debug', '-d']):
        return logging.DEBUG
    else:
        return logging.INFO

def getConfig():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config

if __name__ == "__main__":
    setUp_Logger( getLoggingLevel() )
    logger = logging.getLogger('testingBar')
    CONFIG = getConfig()
    logger.info('Interpreter configuration:\n' + str(CONFIG) )

    root = tk.Tk()
    root.title("testingBar") # pequeño Gran interprete

    menu = menuBar.MenuBar( root )
    menu.setUp( CONFIG )
    root.config( menu=menu )

    root.geometry("250x0")
    root.resizable(1, 0)
    root.mainloop()
