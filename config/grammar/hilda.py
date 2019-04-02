def grammar():
    return [
        'matchClosingTag',
        'valueType',
        'typeId',
        'variableOperation',
        'method',
        'arrayAccess',
        'expression',
        'complement',
        'aritmeticOperator',
        'logicOperator',
        'comparisonOperator',
        'conditionalOperation',
        'conditionalOperator',
        'progStructure',
        'name',
        'areThereConst',
        'defConst',
        'moreConst',
        'areThereArray',
        'defArray',
        'arrayElement',
        'moreArrayElement',
        'moreArray',
        'body',
        'instruction',
        'moreInstruction',
        'asignacion',
        'thereIsArrayAssigment',
        'functionCall',
        'parameter',
        'moreParameter',
        'si',
        'sino',
        'para',
        'ctrlVariable',
        'ctrlAssigment',
        'stepType',
        'mientras'
    ]

def matchClosingTag(self):
    self.logger.info("Searching for closing tag...")
    self.logger.info("Starting at token:\t"+str(self.token))
    open = 1
    while( True ):
        if( self.token['lexeme']  in ['SI', 'PARA', 'MIENTRAS'] ):
            open += 1
        elif( self.token['lexeme']  == 'FIN' ):
            open -= 1
            if( open == 0 ):
                break

        try:
            self.nextToken()
        except EndOfFileException as ex:
            error_msg = "Mismatching closing reserved word,"
            error_msg += " <FIN> not found."
            self.error(error_msg)

    self.logger.info("Ended search for closing tag...")

def valueType(self):
    value = self.token
    self.match( ['entero', 'caracter'] )
    return {'type':value['type'], 'value':value['lexeme']}

def typeId(self):
    if(self.token['type'] in ['entero', 'caracter']):
        value = self.valueType()
        self.logger.debug("Getted type:\t"+str(value))
    elif(self.token['type'] == 'id'):
        id = self.token
        self.match('id')
        value = self.variableOperation( id )
        if(value is None):
            value = self.semantic.getVarValue( {'id':id['lexeme']} )
            value = {'id':id['lexeme'], 'value':value}
        self.logger.debug("Getted id and value:\t"+str(value))

    return value

def variableOperation(self, id):
    self.logger.info("Matching for variable operation.")
    if(self.token['type'] == 'corchete_a'):
        return self.arrayAccess(id)
    elif(self.token['type'] == 'punto'):
        return self.method(id)
    self.logger.info("There's no variable operation.")

def method(self, id):
    self.match('punto')
    method = self.token
    self.match('id')
    value = self.semantic.getVarValue( {'id':id['lexeme'], 'method':method} )
    return {'id':id, 'value':value}

def arrayAccess(self, id):
    self.match('corchete_a')
    index = self.expression()
    value = self.semantic.getVarValue( {'id':id['lexeme'], 'index':index} )
    self.match('corchete_c')
    return {'id':id, 'index':index, 'value':value}

def expression(self):
    self.logger.info("Matching for expression.")
    left = self.typeId()
    left = left['value'] if 'id' in left else left
    complement = self.complement()
    if(complement is not None):
        complement['left'] = left
        result = self.semantic.solveExpr( complement )
    else:
        result = left
    return result

def complement(self):
    if(self.token['type'] in ['mas', 'menos', 'mult', 'div'] or self.token['lexeme'] == 'MOD'):
        line = self.token['line']
        operation = self.aritmeticOperator()
        right = self.typeId()
        right = right['value'] if 'id' in right else right
        return {'operator':operation, 'right':right, 'line':line}

def aritmeticOperator(self):
    operator = self.token
    if(self.token['type'] in ['mas', 'menos', 'mult', 'div']):
        self.match( ['mas', 'menos', 'mult', 'div'] )
    else:
        self.match( ('reserved_word', 'MOD') )
    return operator

def logicOperator(self):
    operator = self.token
    self.match(['and', 'or'])
    return operator

def comparisonOperator(self):
    operator = self.token
    self.match(['menor', 'menor_igual', 'mayor', 'mayor_igual', 'igual', 'diferente'])
    return operator

def conditionalOperation(self, solve=True):
    condition = {}

    if(self.token['lexeme'] == 'not'):
        selt.match( ('reserved_word','not') )
        condition['negate'] = True

    token = self.typeId()
    condition['left'] = token['value'] if 'value' in token and 'value' in token['value'] else token
    condition['operator'] = self.conditionalOperator()
    token = self.typeId()
    condition['right'] = token['value'] if 'value' in token and 'value' in token['value'] else token

    if( solve ):
        return self.semantic.resolveCondition( condition )
    else:
        return condition

def conditionalOperator(self):
    if(self.token['lexeme'] in ['and', 'or']):
        return self.logicOperator()
    else:
        return self.comparisonOperator()

def progStructure(self):
    self.name()
    self.areThereConst()
    self.areThereArray()
    self.match( ('reserved_word', 'INICIO') )
    self.body()
    self.match( ('reserved_word', 'FIN') )

def name(self):
    self.match( ('reserved_word', 'PROGRAMA') )
    self.match( 'id' )

#1_CONSTANTES
def areThereConst(self):
    if(self.token['lexeme'] == 'CONSTANTES'):
        self.match( ('reserved_word', 'CONSTANTES') )
        self.defConst()

def defConst(self):
    var_def = {}
    self.logger.info("Defining constant.")
    var_def['id'] = self.token['lexeme']
    self.match('id')
    self.match('asigna')
    var_def['value'] = self.valueType()
    self.logger.debug(var_def)
    self.semantic.constDef( var_def )
    self.moreConst()

def moreConst(self):
    if( self.token['type'] == 'id' ):
        self.defConst()
#0_CONSTANTES

#1_ARREGLO
def areThereArray(self):
    if(self.token['lexeme'] == 'ARREGLOS'):
        self.match( ('reserved_word', 'ARREGLOS') )
        self.defArray()

def defArray(self):
    self.logger.info("Defining array.")
    var_def = {}
    var_def['id'] = self.token['lexeme']
    self.match('id')
    self.match('asigna')
    self.match('llave_a')
    var_def['value'] = self.arrayElement()
    self.match('llave_c')
    self.logger.debug(var_def)
    self.semantic.arrayDef(var_def)
    self.moreArray()

def arrayElement(self):
    value = []
    value.append( self.valueType() )
    if(self.token['type'] == 'coma'):
        value.extend( self.moreArrayElement() )

    return value

def moreArrayElement(self):
    self.match('coma')
    if(self.token['type'] in ['entero', 'caracter']):
        return self.arrayElement()

def moreArray(self):
    if( self.token['type'] == 'id' ):
        return self.defArray()
#0_ARREGLO

def body(self, errase_created_vars=True):
    self.logger.info( f"Body... [errase_created_vars:{errase_created_vars}]" )

    created_vars = self.instruction( errase_created_vars )

    if( errase_created_vars ):
        self.symbols_table.popVar(created_vars)
        created_vars = 0

    self.logger.info("Body end. Created variables: "+str(created_vars))
    return created_vars

def instruction(self, errase_created_vars):
    self.logger.info("Instruction checking...")

    created_vars = 0
    if(self.token['type'] == 'function'):
        self.functionCall()
        self.match('punto_coma')
    elif(self.token['type'] == 'reserved_word'):
        if(self.token['lexeme'] == 'SI'):
            created_vars = self.si(errase_created_vars)
        elif(self.token['lexeme'] == 'PARA'):
            self.para(errase_created_vars)
        elif(self.token['lexeme'] == 'MIENTRAS'):
            self.mientras(errase_created_vars)
        else:
            error_msg = "Expecting one of the next reserved word: SI, PARA or MIENTRAS"
            error_msg += f" Found: {self.token['lexeme']}"
            self.error( error_msg )
    elif(self.token['type'] == 'id'):
        created_vars = self.asignacion()
        self.match('punto_coma')
    else:
        self.error("Unknown instruction:\t"+str(self.token['lexeme']))


    self.logger.info("Instruction checking ended...")
    created_vars = 0 if created_vars is None else created_vars
    return created_vars+self.moreInstruction(errase_created_vars)

def moreInstruction(self, errase_created_vars):
    if( self.token['type'] in ['function', 'id'] or self.token['lexeme'] in ['PARA', 'MIENTRAS', 'SI']):
        return self.instruction(errase_created_vars)

    return 0

def asignacion(self):
    assigment_prototype = {}
    self.logger.debug('Asigmancion...')
    token = self.match('id')
    assigment_prototype['id'] = token['lexeme']
    array = self.thereIsArrayAssigment( token )
    self.match('asigna')
    assigment_prototype['value'] = self.expression()

    if( array ):
        assigment_prototype['index'] = array['index']
        return self.semantic.assigment( assigment_prototype )
    else:
        return self.semantic.assigment( assigment_prototype )

def thereIsArrayAssigment(self, id):
    if( self.token['type'] == 'corchete_a' ):
        return self.arrayAccess( id )

def functionCall(self):
    func_call = {}
    self.logger.info('Calling function')

    func_call['name'] = self.token['lexeme']
    self.match('function')

    self.match( 'parentesis_a' )
    func_call['parameters'] = self.parameter()
    self.match( 'parentesis_c' )

    self.logger.debug( "Function call:"+str(func_call) )
    if( not self.semantic.buildInFunctions( func_call ) ):
        self.semantic.analyze( func_call )

def parameter(self):
    parameters = []

    parameters.append( self.typeId() )
    if(self.token['type'] == 'coma'):
        parameters.extend( self.moreParameter() )

    return parameters

def moreParameter(self):
    if(self.token['type'] in ['entero', 'caracter', 'id']):
        self.match('coma')
        return self.parameter()

def si(self, errase_created_vars):
    self.logger.info("<SI> call")
    self.match( ('reserved_word', 'SI') )
    self.match( 'parentesis_a' )
    condition = self.conditionalOperation()
    self.match( 'parentesis_c' )
    self.match( ('reserved_word', 'ENTONCES') )
    if( condition ):
        created_vars = self.body( errase_created_vars )
    else:
        created_vars = self.sino( errase_created_vars )
    self.match( ('reserved_word', 'FIN') )

    return created_vars

def sino(self, errase_created_vars):
    self.logger.info("Matching <SINO>")
    if( self.token['lexeme'] == 'SINO' ):
        self.logger.info("<SINO> call")
        self.match( ('reserved_word', 'SINO') )
        return self.body(errase_created_vars)
    else:
        self.matchClosingTag( )

def para(self, errase_created_vars):
    self.logger.info('<PARA> call')
    para = {}
    self.match( ('reserved_word', 'PARA') )
    para['ctrl_var'] = self.ctrlVariable()
    self.match( ('reserved_word', 'HASTA') )
    para['to'] = self.typeId()
    self.logger.debug("Para[HASTA]:\t"+str(para['to']) )
    self.match( ('reserved_word', 'PASO') )
    para['step'] = self.stepType()
    self.match( ('reserved_word', 'HACER'), dry=True )

    self.logger.debug("<PARA> prototype:\t"+str(para))

    body_start = {
                    'row':self.lexer.source.getRowIndex(),
                    'column':self.lexer.source.getColumIndex()
                }
    var_debt, para = self.semantic.paraInit(para)
    while( True ):
        self.logger.info("<PARA> evaluating iteration condition.")
        if( self.semantic.paraIter(para) ):
            self.logger.info("<PARA> Iteration")
            self.logger.debug("Jumping to:"+str(body_start['row'])+','+str(body_start['column']))
            self.lexer.source.setCoordinates(body_start['row'], body_start['column'])
            self.nextToken()
            var_debt += self.body(errase_created_vars=False)
        else:
            self.matchClosingTag( )
            break

    if( errase_created_vars ):
        self.symbols_table.popVar( var_debt )
    self.logger.debug( "Current source coordinates:\t"+self.lexer.source.getCoordinates() )
    self.match( ('reserved_word', 'FIN') )
    self.logger.debug("Ended PARA:\t"+str(para))

def ctrlVariable(self):
    ctrl_var = {'id':self.token['lexeme']}
    self.match('id')
    value = self.ctrlAssigment()
    if(value is not None):
        ctrl_var['value'] = value

    return ctrl_var

def ctrlAssigment(self):
    if(self.token['type'] == 'asigna'):
        self.match('asigna')
        return self.expression()

def stepType(self):
    step = {}
    step['type'] = self.token['lexeme']
    if(self.token['type'] == 'mas'):
        self.match('mas')
    elif(self.token['type'] == 'menos'):
        self.match('menos')

    step['value'] = {'type':self.token['type'], 'value':self.token['lexeme']}
    self.match('entero')

    return step

def mientras(self, errase_created_vars):
    self.logger.info("<MIENTRAS> call")
    self.match( ('reserved_word', 'MIENTRAS') )
    condition = self.conditionalOperation(solve=False)
    self.match( ('reserved_word', 'HACER'), dry=True )

    body_start = {
                    'row':self.lexer.source.getRowIndex(),
                    'column':self.lexer.source.getColumIndex()
                }
    var_debt = 0
    while( self.semantic.resolveCondition(condition) ):
        self.logger.debug("<MIENTRAS> iteration")
        self.lexer.source.setCoordinates(body_start['row'], body_start['column'])
        self.nextToken()
        var_debt += self.body(errase_created_vars=False)

    if( errase_created_vars ):
        self.symbols_table.popVar( var_debt )
    self.match( ('reserved_word', 'FIN') )
