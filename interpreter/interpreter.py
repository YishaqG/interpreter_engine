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
        self.symbols_table.loadConfigData( r.getData() )

    def reloadSyms(self, syms_table_descriptor):
        self.CONFIG['symbols_table'] = syms_table_descriptor
        r = reader.Reader( syms_table_descriptor )
        self.symbols_table.loadConfigData( r.getData() )
        self.logger.debug( self.symbols_table )

    def reloadAutomata(self, automata_descriptor):
        self.CONFIG['automata'] = automata_descriptor
        r = reader.Reader( automata_descriptor )
        self.automata.loadConfigData( r.getData() )
        self.logger.debug(self.automata)

    def reloadGrammar(self, grammar_descriptor):
        self.CONFIG['grammar'] = grammar_descriptor
        self.sintaxer = sintaxer.Sintaxer( self.symbols_table,
                                            self.lexer, self.semantic )
        self.sintaxer.setGrammar( grammar_descriptor )

    def reloadSemantic(self, semantic_descriptor):
        self.CONFIG['semantic'] = semantic_descriptor
        self.semantic = semantic.Semantic( self.symbols_table )
        self.semantic.setSemantic( semantic_descriptor )
        self.sintaxer.semantic = self.semantic

    def saveConfig(self):
        with open(self.CONFIG['SAVE_AS'], 'w') as outfile:
            json.dump(config, outfile)

    def run(self, source, show_exception=True):
        self.lexer.setSource( Container.Container(source) )

        if( show_exception ):
            try:
                self.sintaxer.nextToken()
                self.sintaxer.progStructure()
            except Container.EndOfFileException as ex:
                self.logger.debug("End of file.")
            finally:
                self.logger.debug("Reseting interpreter configuration.")
                self.resetConfig()
        else:
            try:
                self.sintaxer.nextToken()
                self.sintaxer.progStructure()
            except Container.EndOfFileException as ex:
                self.logger.debug("End of file.")
            except Exception as ex:
                pass
            finally:
                self.logger.debug("Reseting interpreter configuration.")
                self.resetConfig()


        self.logger.debug("="*80)
        self.logger.info("Analysis ended.")
        self.logger.debug("="*80)
