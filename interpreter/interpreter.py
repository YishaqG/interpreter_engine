import json, logging
from interpreter import lexer, symbolsTable, sintaxer, semantic, Container, reader, automata

class Interpreter(object):
    def __init__(self, config):
        self.logger = logging.getLogger('Interpreter')
        self.CONFIG = config
        self.loadConfig()

    def setConfig(self, config):
        self.CONFIG = config
        self.loadConfig()

    def loadConfig(self):
        r = reader.Reader( self.CONFIG['symbols_table'] )
        self.symbols_table = symbolsTable.SymbolsTable( r.getData() )

        r.setPath( self.CONFIG['automata'] )
        self.automata = automata.Automata( r.getData() )

        self.lexer = lexer.Lexer( self.symbols_table, self.automata )

        self.semantic = semantic.Semantic( self.symbols_table )
        self.sintaxer = sintaxer.Sintaxer( self.symbols_table,
                                            self.lexer, self.semantic )

        self.sintaxer.setGrammar( self.CONFIG['grammar'] )
        self.semantic.setSemantic( self.CONFIG['semantic'] )

    def resetConfig(self):
        r = reader.Reader( self.CONFIG['symbols_table'] )
        self.symbols_table = symbolsTable.SymbolsTable( r.getData() )

        self.lexer.setSymbolsTable(self.symbols_table)

        self.semantic = semantic.Semantic( self.symbols_table )
        self.sintaxer.setGrammar( self.CONFIG['grammar'] )
        self.semantic.setSemantic( self.CONFIG['semantic'] )

    def reloadSyms(self, symbols_table):
        r = reader.Reader( symbols_table )
        self.symbols_table.loadConfigData( r.getData() )
        self.logger.debug(self.symbols_table)

    def reloadAutomata(self, automata):
        r = reader.Reader( automata )
        self.automata.loadConfigData( r.getData() )
        self.logger.debug(self.automata)

    def reloadGrammar(self, grammar):
        self.sintaxer = sintaxer.Sintaxer( self.symbols_table,
                                            self.lexer, self.semantic )
        self.sintaxer.setGrammar( grammar )

    def reloadSemantic(self, semantic):
        self.semantic.setSemantic( semantic )

    def saveConfig(self):
        with open(self.CONFIG['SAVE_AS'], 'w') as outfile:
            json.dump(config, outfile)

    def run(self, source):
        self.lexer.setSource( Container.Container(source) )
        try:
            self.sintaxer.nextToken()
            self.sintaxer.progStructure()
        except Container.EndOfFileException as ex:
            self.logger.Info("Analysis ended.")

        self.resetConfig()
