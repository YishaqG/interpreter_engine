import logging, re, types, sys
from importlib import util
from interpreter.Container import EndOfFileException
from pathlib import Path

class Sintaxer(object):

    def __init__(self, symbols_table, lexer, semantic):
        self.logger = logging.getLogger('Sintaxer')
        self.symbols_table = symbols_table
        self.lexer = lexer
        self.semantic = semantic
        self.token = None

    def nextToken(self):
        self.token = self.lexer.nextToken()
        self.logger.debug("Current token:\t" + str(self.token))

    def error(self, expected):
        error_msg = "Sintaxer:ERROR:"
        error_msg += f"Expected {expected} found {self.token}"
        error_msg += f" at line {self.token['line']}"
        print(error_msg)
        raise SyntacticError()

    def match(self, expected, dry=False):
        """
            Consume the current token if it matches the expected one
            There are 3 variants of the expected token:
                -Classified-token: when the type & the lexeme are already known.
                    The lexeme is predefined.
                -List of types: the token could be one of the given types.
                    The lexeme can be anything, therefor unknown.
                -Type: most be the given type.
                    The lexeme can be anything, therefor unknown.
        """
        if( isinstance(expected, tuple) ):
            # {type,lexeme}
            condition = (expected[0] == self.token['type'])
            condition = condition and (expected[1] == self.token['lexeme'])
        elif( isinstance(expected, list) ):
            # [type1, type2, ..., typeN]
            condition = (self.token['type'] in expected)
        else:
            condition = (expected == self.token['type'])

        if( condition ):
            if( not dry):
                self.nextToken()
        else:
            self.error(expected)



    def gotoNextToken(self, to):
        while( True ):
            condition = (to[0] == self.token['type'])
            condition = condition and (to[1] == self.token['lexeme'])
            if( condition ):
                break
            else:
                self.nextToken()

    def setGrammar(self, path):
        self.logger.info("Loading grammar...")
        try:
            path = Path(path).resolve()
            spec = util.spec_from_file_location(path.name, path)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as ex:
            self.logger.error( str(ex) )
            self.logger.error("Unable to load grammar.")

        if( 'grammar' in list(module.__dict__.keys()) ):
            functions = getattr(module, 'grammar')()
            self.logger.debug( "Grammar:\t"+str(functions) )
            for function in functions:
                setattr(self, function, types.MethodType(getattr(module, function), self))
            self.logger.info("Grammar loaded...")
        else:
            self.logger.error("Define the function >grammar< at your grammar implementation.")

    def run(self, source):
        self.lexer.setSource( Container.Container(source) )
        self.semantic.stand_by = True
        self.logger.info("Syntactic analysis running...")
        try:
            self.nextToken()
            self.progStructure()
        except EndOfFileException as ex:
            self.logger.info("Analysis ended.")
        except Exception as ex:
            self.logger.error( str(ex) )
        finally:
            self.semantic.stand_by = False

class SyntacticError(Exception):
    def __init__(self):
        pass

    def buildMessage(expected, token, at_line):
        error_msg = "Expected %r found %r" %(expected, token)
        error_msg += " at line %r" % at_line
        return error_msg
