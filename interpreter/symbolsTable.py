import logging
from . import configData

class SymbolsTable(object):

    _slots_ = ['table', 'logger']

    def __init__(self, data):
        self.logger = logging.getLogger('SymbolsTable')
        self.setUpTable()

        self.loadConfigData(data)

    def setUpTable(self):
        self.table = {}

        self.table[ 'tokens' ] = {}
        self.table[ 'reserved_words' ] = []
        self.table[ 'data_types' ] = []
        self.table[ 'functions' ] = {}
        self.table[ 'constants' ] = {}
        self.table[ 'identifiers' ] = {}

    def __str__(self):
        return "Symbols Table:\t"+str(self.table)+"\n"

    def loadConfigData(self, data):
        configData.validateStructure( ['tokens'], data, '<SymbolsTable>' )
        self.setUpTable()

        self.loadTokens( data[ 'tokens' ] )
        if('reserved_words' in data):
            self.table['reserved_words'] = list(data[ 'reserved_words' ][0])
        if('data_types' in data):
            self.table['data_types'] = list(data[ 'data_types' ][0])
        if('functions' in data):
            self.loadFunctions( data[ 'functions' ] )
        if('constants' in data):
            self.loadConst( data[ 'constants' ] )

#1_Tokens
    def loadTokens(self, data):
        for token in data:
            self.table['tokens'][token[0]] = token[1:]

    def getToken(self, to_get):
        raw_token = self.table['tokens'][to_get]
        token = {'name':raw_token[0], 'recoil':raw_token[1]}

        self.logger.debug("Found token:\t"+str(token))
        return token
#0_Tokens

#1_Reserved words
    def isReservedWord(self, key_word):
        return key_word in self.table['reserved_words']
#0_Reserved words

#1_Data types
#0_Data types

#1_Functions
    def loadFunctions(self, functions):
        for function in functions:
            self.addFunction( function[0], function[1:] )

    def addFunction(self, name, parameters):
        if( not isinstance(parameters, list) ):
            raise TypeError( parameters )
        for type in parameters:
            if( not type in self.table['data_types'] ):
                error_msg = "Value=%r, not in %r" %(type, self.table['data_types'])
                raise LookupError(error_msg)

        self.table['functions'][name] = parameters

    def isFunction(self, name):
        return name in self.table['functions']

    def getFunctionParameters(self, name):
        return self.table['functions'][name]
#0_Functions

#1_Identifiers
    def addId(self, name, type, value):
        """
            Isn't necessary check for the existence of the ID since if exist
            its value is modified and if not the variable is created
        """
        msg = f"Indexing token <{name}> "
        msg += f"of type <{type}> and value <{value}>"
        self.logger.debug(msg)
        self.table['identifiers'][name] = {'type':type, 'value':value}

    def getId(self, name):
        if(name in self.table['identifiers']):
            return self.table['identifiers'][name]
        else:
            return None

    def popVar(self, ammount_to_pop):
        vars = list( self.table['identifiers'] )
        popped = 0
        for id in reversed(vars):
            if(popped > ammount_to_pop-1):
                break

            del self.table['identifiers'][id]
            popped += 1

#0_Identifiers

#1_Constants
    def loadConst(self, constants):
        for const in constants:
            self.addConst(const[0], const[1], const[2])

    def addConst(self, name, type, value):
        if(name in self.table['constants']):
            raise automata.RepeatedValueException()
        else:
            self.table['constants'][name] = {'type':type, 'value':value}

    def getConst(self, name):
        if(name in self.table['constants']):
            return self.table['constants'][name]
        else:
            return None
#0_Constants
