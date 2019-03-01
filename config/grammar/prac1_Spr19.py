def grammar():
    return [
        'progStructure',
        'name',
        'body',
        'instruction',
        'moreInstruction',
        'functionCall',
        'parameter',
        'moreParameter',
        'parameterType'
    ]

def progStructure(self):
    self.name()
    self.match( ('reserved_word', 'INICIO') )
    self.body()
    self.match( ('reserved_word', 'FIN') )

def name(self):
    self.match( ('reserved_word', 'PROGRAMA') )
    self.match( 'id' )

def body(self):
    self.instruction()
    self.moreInstruction()

def instruction(self):
    self.functionCall()

def moreInstruction(self):
    if( self.token['type'] == 'function' ):
        self.body()

def functionCall(self):
    func_call = {}
    self.logger.info('function')

    func_call['type'] = self.token['type']
    func_call['name'] = self.token['lexeme']
    self.match('function')

    self.match('parentesis_a')
    func_call['parameters'] = self.parameter()
    self.match('parentesis_c')

    self.semantic.analyze(func_call)

def parameter(self):
    parameters = []

    parameters.append( self.parameterType() )
    if(self.token['type'] == 'coma'):
        self.match('coma')
        parameters.extend( self.moreParameter() )
    print(parameters)

    return parameters

def moreParameter(self):
    if( self.token['type'] in ['entero', 'cadena', 'id'] ):
        return self.parameter()

def parameterType(self):
    value = (self.token['type'], self.token['lexeme'])
    self.match( ['entero', 'cadena', 'id'] )
    return value
