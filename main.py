#!/usr/bin/env python3

import logging, json, sys, argparse
from importlib import util
from interpreter import interpreter

def setUp_Logger( args ):
    if( args.debug ):
        log_level = logging.DEBUG
    elif(args.info):
        log_level = logging.INFO
    elif(args.error):
        log_level = logging.ERROR

    logging.basicConfig(
            level=log_level,
            format='%(name)s:%(levelname)s: %(message)s'
        )

    if( args.file_write ):
        file_mode = 'w'
    elif( args.file_append ):
        file_mode = 'a'

    fh = logging.FileHandler( 'logging.log', mode=file_mode )
    fh.setLevel( logging.DEBUG )
    formatter = logging.Formatter('%(name)s:%(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    logging.getLogger('').addHandler(fh) #Add the handler to the root logger

def setUp_argparser():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--testing-bar", action='store_true', help="Start the graphical interface")
    mode.add_argument("-in", "--input", help="File path")
    loggin_lvl = parser.add_mutually_exclusive_group()
    loggin_lvl.add_argument("-d", "--debug", action='store_true', help="Set logging level to: DEBUG")
    loggin_lvl.add_argument("-i", "--info", action='store_true', help="Set logging level to: INFO")
    loggin_lvl.add_argument("-e", "--error", action='store_true', help="Set logging level to: ERROR", default=logging.ERROR)
    file_mode = parser.add_mutually_exclusive_group()
    file_mode.add_argument("-fw", "--file-write", action='store_true', help="Set logging file to: WRITE")
    file_mode.add_argument("-fa", "--file-append", action='store_true', help="Set logging file to: APPEND", default='a')
    return parser.parse_args()

def getConfig():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config

def testing_bar( CONFIG ):
    tk = __import__( 'tkinter' )
    spec = util.spec_from_file_location('menuBar', './views/menuBar.py')
    menuBar = util.module_from_spec(spec)
    spec.loader.exec_module(menuBar)

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

if __name__ == "__main__":
    args = setUp_argparser()
    setUp_Logger( args )
    CONFIG = getConfig()

    if( args.testing_bar ):
        testing_bar(CONFIG)
    else:
        inter = interpreter.Interpreter( CONFIG['LANGUAGE'][CONFIG['DEFAULT_LANGUAGE']] )
        with open( args.input, 'r' ) as f:
            inter.run( f.read(), True if args.debug or args.info else False )
