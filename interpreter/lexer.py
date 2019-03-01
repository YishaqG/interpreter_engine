import logging
from enum import Enum
from . import automata,symbolsTable,Container


class Lexer(object):

    _slots_ = ['logger','source', 'automata', 'symbols_table']

    def __init__(self, symbols_table=None, automata=None, source=None):
        self.logger = logging.getLogger('Lexer')

        self.setSymbolsTable( symbols_table ) if symbols_table is not None else None
        self.setSource(source) if source is not None else None
        self.setAutomata(automata) if automata is not None else None

        self.builtIn_types = ['reserved_word', 'function']

    def error(self, msg):
        error_msg = "Lexer:ERROR:"
        error_msg += msg
        raise LexicError

    def setSource(self, source):
        if( isinstance(source, Container.Container) ):
            self.source = source
        else:
            raise TypeError(source)

    def setSymbolsTable(self, table):
        if( isinstance(table, symbolsTable.SymbolsTable) ):
            self.symbols_table = table
        else:
            raise TypeError(table)

    def setAutomata(self, auto):
        if( isinstance(auto, automata.Automata) ):
            self.automata = auto
        else:
            raise TypeError(auto)

    def nextChar(self):
        current_char = self.source.nextChar()
        while( current_char.isspace() ):
            current_char = self.source.nextChar()
        self.logger.debug("Update current character:\t"+current_char)
        return current_char

    def _whiteSpaceHandler(self):
        current_char = self.source.nextChar()
        while( current_char.isspace() ):
            current_char = self.source.nextChar()
        self.source.recoilChar(1)

    def nextToken(self):
        try:
            result = self._nextLexeme()
        except ValueError as e:
            error_msg = "Invalid character found at {self.source.getCoordinates()}.\n"
            error_msg += str(e)
            self.error(error_msg)
        except automata.BadSequenceException as e:
            error_msg = f"Invalid sequence found at {self.source.getCoordinates()}.\n"
            error_msg += str(e)
            self.error(error_msg)

        return self._classify(result)

    def _nextLexeme(self):
        self._whiteSpaceHandler()
        self.automata.restart()

        current_char = self.source.nextChar()
        evaluation = self.automata.evaluate( current_char.lower() )
        lexeme = current_char

        if( evaluation is None ): # No final state
            while( True ):
                current_char = self.source.nextChar()
                lexeme += current_char

                if( current_char.isspace() ):
                    evaluation = self.automata.evaluate( None )
                    break
                elif(current_char == '\''):
                    lexeme = self.getCharacter()
                    evaluation = 'caracter'

                try:
                    evaluation = self.automata.evaluate( current_char.lower() )
                except automata.BadSequenceException:
                    if( evaluation is not None ):
                        break
                    else:
                        pass
                except ValueError:
                    evaluation = self.automata.evaluate( None )
                    break

                if( self.symbols_table.isReservedWord(lexeme) ):
                    evaluation = 'reserved_word'
                    break
                elif( self.symbols_table.isFunction(lexeme) ):
                    evaluation = 'function'
                    break
                elif(evaluation is not None):
                    break

        return {'id':evaluation, 'lexeme':lexeme}

    def getCharacter(self):
        current_char = self.source.nextChar()

        if(self.source.nextChar() != '\''):
            error_msg = "Invalid sequence found at {0}\n".format(
                    self.source.getCoordinates()
                )
            self.error(error_msg)

        return current_char


    def _classify(self, data):
        tuple = None
        self.logger.info("Classifying lexeme...")
        self.logger.debug("Raw-token:\t"+str(data))

        if( data['id'] not in ['reserved_word', 'function', 'caracter'] ):
            token_info = self.symbols_table.getToken( data['id'] )

            recoil = int(token_info['recoil'])
            self.source.recoilChar( recoil )

            data['id'] = token_info['name']
            data['lexeme'] = data['lexeme'][:-recoil] if recoil > 0 else data['lexeme']

        token = {
                'type': data['id'],
                'lexeme': data['lexeme'],
                'line': self.source.getRowIndex()
            }

        self.logger.debug("Classified-token:\t"+str(data))
        return token

        return current_char

    def run(self, source):
        self.setSource( Container.Container(source) )
        try:
            while True:
                print( "Token:\t"+str(self.nextToken()) )
        except EndOfFileException as ex:
            self.logger.info("Analysis ended.")

class LexicError(Exception):
    def __init__(self):
        pass
