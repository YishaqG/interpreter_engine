import tkinter as tk
from tkinter.filedialog import *
from tkinter.messagebox import *
import sys, logging
from interpreter import interpreter, Container, semantic

class MenuBar(tk.Menu):
    def __init__(self, parent):
        super().__init__(parent)

    def setUp(self, CONFIG):
        self.file = File()
        self._setUp_File()
        self._setUp_Interpreter(CONFIG)
        self._setUp_Run()

    def _setUp_File(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Set Source Path", command=self.file.openFile)

        self.add_cascade(label="File", menu=menu)

    def _setUp_Interpreter(self, CONFIG):
        self.interpreter = Interpreter(self.file, CONFIG)

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Select", command=self.interpreter.loadLenguage)

        menu.add_separator()

        submenu = tk.Menu(self, tearoff=0)
        submenu.add_command(label="Automata", command=self.interpreter.loadAutomata)
        submenu.add_command(label="Symbols Table", command=self.interpreter.loadSymbolsTable)
        submenu.add_command(label="Grammar", command=self.interpreter.loadGrammar)
        submenu.add_command(label="Semantic", command=self.interpreter.loadSemantic)
        menu.add_cascade(label="Configurate", menu=submenu)

        self.add_cascade(label="Interpreter", menu=menu)
        return interpreter

    def _setUp_Run(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Interpreter", command=self.interpreter.runInterpreter)
        menu.add_separator()
        menu.add_command(label="Lexer Analizer", command=self.interpreter.runLexer)
        menu.add_command(label="Sintactic Analizer", command=self.interpreter.runSintactic)
        self.add_cascade(label="Run", menu=menu)

class File():
    def __init__(self):
        pass

    def openFile(self):
        f = askopenfile(initialdir="tests/input/", title="Select source", mode='r')
        print(f.name)
        self.path = f.name

class Interpreter():
    def __init__(self, file, CONFIG):
        self.file = file
        self.config = CONFIG
        self.interpreter = interpreter.Interpreter( self.config['LANGUAGE'][self.config['DEFAULT_LANGUAGE']] )

    def loadAutomata(self):
        f = askopenfile(initialdir="config/automata/", title="Select automata", mode='r')
        self.interpreter.reloadAutomata( f.name )

    def loadSymbolsTable(self):
        f = askopenfile(initialdir="config/symbols_table/", title="Select symbols table", mode='r')
        self.interpreter.reloadSyms( f.name )

    def loadGrammar(self):
        f = askopenfile(initialdir="config/grammar", title="Select grammar", mode='r')
        self.interpreter.reloadGrammar( f.name )

    def loadSemantic(self):
        f = askopenfile(initialdir="config/semantic/", title="Select semantic", mode='r')
        self.interpreter.reloadSemantic( f.name )

    def loadLenguage():
        pass

    def addLenguage():
        pass

    def runInterpreter(self):
        with open(self.file.path, 'r') as f:
            self.interpreter.run( f.read() )

    def runLexer(self):
        with open(self.file.path, 'r') as f:
            self.interpreter.lexer.run( f.read() )

    def runSintactic(self):
        with open(self.file.path, 'r') as f:
            self.interpreter.sintaxer.run( f.read() )

if __name__ == "__main__":
	print ("Please run 'test_bar.py'")
