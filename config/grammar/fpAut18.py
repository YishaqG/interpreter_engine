ARREGLOS = ('reserved_word', 'ARREGLOS')
PROGRAMA = ('reserved_word', 'PROGRAMA')
CONSTANTES = ('reserved_word', 'CONSTANTES')
HASTA = ('reserved_word', 'HASTA')
HACER = ('reserved_word', 'HACER')
MOD = ('reserved_word', 'MOD')
ENTONCES = ('reserved_word', 'ENTONCES')
INICIO = ('reserved_word', 'INICIO')
FIN = ('reserved_word', 'FIN')
PARA = ('reserved_word', 'PARA')
SI = ('reserved_word', 'SI')
SINO = ('reserved_word', 'NOSI')
PASO = ('reserved_word', 'PASO')

def checkProgram(self):
    if(self.current_token == PROGRAMA):
        self.checkHeader()
        self.logger.info("Header Checked")
        self.areThereConsts()
        self.logger.info("Constants Checked")
        self.areThereArrays()
        self.logger.info("Arrays Checked")
        if(self.current_token == INICIO):
            self.nextToken()
        else:
            self.error(INICIO)
        self.logger.info("Program start")
        self.checkBody()
        self.logger.info("Body checked")
        if(self.current_token == FIN):
            self.nextToken()
        else:
            self.error(FIN)
        self.logger.info("Program end")
    else:
        self.error(PROGRAMA)

def checkHeader(self):
    if(self.current_token == PROGRAMA):
        self.nextToken()
        self.match( 'id' )
    else:
        self.error(PROGRAMA)

def assignment(self):
    temp = self.idArray()
    self.match('asigna')

    return temp

def areThereConsts(self):
    if(self.current_token == CONSTANTES):
        self.nextToken()
        self.defConst()
    elif(self.current_token == ARREGLOS):
        return None
    else:
        self.error(ARREGLOS)

def defConst(self):
    temp = []
    temp += self.assignment()
    temp.append( self.typesValues() )
    self.logger.debug( 'Const' + str(temp))
    self.semantic.defConst(temp)

    self.nextConst()

def nextConst(self):
    if(self.current_token == ARREGLOS):
        return None

    self.defConst()

def areThereArrays(self):
    if(self.current_token == ARREGLOS):
        self.nextToken()
        self.defArray()
    elif(self.current_token == INICIO):
        return None
    else:
        self.error([ARREGLOS, INICIO])

def defArray(self):
    temp = []
    temp += self.assignment()
    self.match('llave_a')
    temp2 = []
    temp2.append( self.typesId() )
    temp2 += self.nData()
    temp.append(temp2)
    self.match('llave_c')
    self.logger.debug('Array' + str(temp))
    self.semantic.defArray(temp)

    self.nArray()

def nData(self):
    if(self.current_token[0] == 'llave_c'):
        return None
    temp = []
    self.match('coma')
    temp.append( self.typesId() )
    hasNData = self.nData()
    if(hasNData is not None):
        temp += hasNData
    return temp

def nArray(self):
    if(self.current_token[0] == 'id'):
        self.defArray()

    elif(self.current_token == INICIO):
        return None

    else:
        self.error(['id', INICIO])

def checkBody(self):
    self.logger.info('checkBody')
    predict = self.current_token[0] in ['id', 'function']
    itIs = self.current_token in [PARA, SI]
    if( predict or itIs ):
        self.instruction()
        self.nInstruction()
    else:
        self.error(['id', 'function', PARA, SI])

def instruction(self):
    self.logger.info('instruction')
    if(self.current_token[0] == 'function'):
        self.function()
    elif(self.current_token == SI):
        self.checkIf()
    elif(self.current_token == PARA):
        self.checkFor()
    elif(self.current_token[0] == 'id'):
        self.checkExpr()
    else:
        self.error( ['function', 'id', SI, PARA] )

def nInstruction(self):
    self.logger.info('nInstruction')
    predict = ['id', 'function']
    itIs = (self.current_token == PARA) or (self.current_token == SI)
    if((self.current_token[0] in predict) or itIs):
        self.checkBody()
    else:
        return None

def function(self):
    temp = []
    self.logger.info('function')
    if(self.current_token[0] == 'function'):
        temp.append( self.current_token )
        self.nextToken()
        self.match('parentesis_a')
        temp.append( self.parameter() )
        self.match('parentesis_c')
        self.match('punto_coma')
        self.logger.debug('FunctiontoSemantic: ' + str(temp))
        self.semantic.transitions(temp)
    else:
        self.error(['function','parentesis_a', 'parentesis_c','punto_coma'])

def parameter(self):
    predict = ['id', 'caracter', 'entero']
    if( self.current_token[0] in predict):
        return self.typesId()
    else:
        self.error( predict )

def checkIf(self):
    temp = []
    self.logger.info('checkIf')
    if(self.current_token == SI):
        self.semantic.transitions(['SI'])
        self.nextToken()
        self.match('parentesis_a')
        temp += self.checkCondition()
        self.match('parentesis_c')
        if(self.current_token == ENTONCES):
            self.logger.debug('ifToSemantic' + str(temp))
            self.semantic.transitions(temp)#Llamado al SI
            self.nextToken()
        else:
            self.error(ENTONCES)
        self.checkBody()
        self.checkElse()
    else:
        self.error([SI,'parentesis_a','parentesis_c', ENTONCES])

def checkElse(self):
    self.logger.info('checkElse')
    if(self.current_token == SINO):
        self.semantic.transitions(['NOSI'])
        self.nextToken()
        self.checkBody()
    elif(self.current_token == FIN):
        self.nextToken()
    else:
        self.error( [SINO, FIN] )

def checkExpr(self):
    temp = []
    self.logger.info('checkExpr')
    temp.append(self.semantic.getIDValue(self.current_token))
    if(self.current_token[0] == 'id'):
        self.match('id')
        temp.append( self.checkSubExpr() )
        self.match('punto_coma')
        self.logger.debug('exprToSemantic' + str(temp))
        self.semantic.expr(temp)
    else:
        self.error('id')

def checkSubExpr(self):
    temp = []
    if(self.current_token[0] == 'asigna'):
        temp += self.add()
    elif(self.current_token[0] == 'corchete_a'):
        temp += self.arrayAccess()
        temp += self.add()
    else:
        self.error(['asigna', 'corchete_a'])

    return temp

def add(self):
    temp = []
    temp2 = []
    if(self.current_token[0] == 'asigna'):
        self.match('asigna')
        temp += self.parametersValues()
        temp2 = self.expr()

        if(temp2 is not None):
            temp += temp2
            r = temp
        else:
            r = temp[0]
    else:
        self.error('asigna')

    return r

def expr(self):
    temp = []
    predict = ['suma', 'div_entera', 'resta', 'mult']
    if((self.current_token[0] in predict) or self.current_token == MOD):
        temp.append( self.checkOp() )
        temp+= self.parametersValues()
    elif( self.current_token[0] in ['punto_coma', 'corchete_c'] ):
        return None
    else:
        self.error( predict + ['punto_coma', 'corchete_c'] + MOD )

    return temp

def checkFor(self):
    temp = []
    self.logger.info('checkFor')
    if(self.current_token == PARA):
        self.semantic.transitions(['PARA'])
        self.nextToken()
        temp += self.variableCtrl()
        if( self.current_token == HASTA):
            self.nextToken()
        else:
            self.error(HASTA)
        temp += self.parametersValues()
        if( self.current_token == PASO):
            self.nextToken()
            temp.append(self.current_token)
        else:
            self.error(PASO)
        self.mm()
        self.match('entero')
        if( self.current_token == HACER):
            self.logger.debug('forToSemantic' + str(temp))
            self.semantic.transitions(temp)#Llamado al para
            self.nextToken()
        else:
            self.error(HACER)
        self.checkBody()
        if( self.current_token == FIN):
            self.nextToken()
        else:
            self.error(FIN)
    else:
        self.error([PARA, HASTA, PASO, HACER, 'entero'])

def variableCtrl(self):
    temp = []
    temp.append( self.match('id') )
    temp += self.ToCtrl()

    return temp

def ToCtrl(self):
    if(self.current_token == HASTA):
        return None

    self.match('asigna')
    return self.parametersValues()

def mm(self):
    temp = self.current_token
    if(self.current_token[0] == 'resta'):
        self.match('resta')
    elif(self.current_token[0] == 'suma'):
        self.match('suma')
    else:
        self.error(['resta', 'suma'])

    return temp

def checkOp(self):
    temp = self.current_token
    if(self.current_token[0] == 'mult'):
        self.match('mult')
    elif(self.current_token[0] == 'div_entera'):
        self.match('div_entera')
    elif(self.current_token[1] == 'MOD'):
        self.nextToken()
    elif(self.current_token[0] == 'suma'):
        self.mm()
    elif(self.current_token[0] == 'resta'):
        self.mm()
    else:
        self.error(['mult', 'div_entera', 'MOD', 'suma', 'resta'])

    return temp

def checkCondition(self):
    temp = []
    if(self.current_token[0] == 'id' or self.current_token[0] == 'caracter' or self.current_token[0] == 'entero'):
        temp += self.parametersValues()
        temp.append( self.condition() )
        temp += self.parametersValues()
    else:
        self.error(['id', 'caracter', 'entero'])

    return temp

def condition(self):
    temp = self.current_token
    if(self.current_token[0] == 'igual_a'):
        self.match('igual_a')
    elif(self.current_token[0] == 'menor'):
        self.match('menor')
    elif(self.current_token[0] == 'menor_igual'):
        self.match('menor_igual')
    elif(self.current_token[0] == 'mayor'):
        self.match('mayor')
    elif(self.current_token[0] == 'mayor_igual'):
        self.match('mayor_igual')
    elif(self.current_token[0] == 'diferente'):
        self.match('diferente')
    else:
        self.error(['igual_a', 'menor', 'menor_igual', 'mayor', 'menor_igual', 'diferente'])

    return temp

def arrayOp(self):
    temp = []
    if(self.current_token[0] == 'punto'):
        temp += self.lenght()
    elif(self.current_token[0] == 'corchete_a'):
        temp += self.arrayAccess()
    else:
        self.error(['punto', 'corchete_a'])

def lenght(self):
    temp = None
    self.match('punto')
    if(self.current_token[1] == 'lenght'):
        temp = self.current_token
        self.nextToken()
    else:
        self.error('lenght')

    return temp

def arrayAccess(self):
    temp = []
    if(self.current_token[0] == 'corchete_a'):
        self.match('corchete_a')
        temp += self.index()
        self.match('corchete_c')
    else:
        self.error(['corchete_a'])

    return temp

def index(self):
    temp  = []
    temp2  = []
    r = []
    if(self.current_token[0] == 'id' or self.current_token[0] == 'caracter' or self.current_token[0] == 'entero'):
        temp += self.parametersValues()
        temp2 = self.expr()
        if(temp2 is not None):
            temp.append(temp2[0])
            temp.append(temp2[1])
            r = self.semantic.expr(temp)
        else:
            r = temp[0]
    else:
        self.error(['id', 'caracter', 'entero'])
    return r

def idArray(self):
    temp = []
    if(self.current_token[0] == 'id'):
        temp.append( self.current_token )
        self.match('id')
        self.arrayPos()
    else:
        self.error(['id'])
    return temp


def arrayPos(self):
    temp = None
    if(self.current_token[0] == 'corchete_a'):
        self.match('corchete_a')
        temp = self.index()
        self.match('corchete_c')
    elif(self.current_token[0] == 'asigna' or self.current_token[0] == 'igual_a' or self.current_token[0] == 'menor'):
        return None
    elif(self.current_token[0] == 'menor_igual' or self.current_token[0] == 'mayor' or self.current_token[0] == 'mayor_igual'):
        return None
    elif(self.current_token[0] == 'diferente' or self.current_token[0] == PASO or self.current_token[0] == 'parentesis_c'):
        return None
    elif(self.current_token[0] == 'corchete_c' or self.current_token[0] == HASTA or self.current_token[0] == FIN or self.current_token[0] == 'id'):
        return None
    elif(self.current_token[0] == 'function' or self.current_token[0] == PARA or self.current_token[0] == SI):
        return None
    else:
        self.error(['TO_DO'])
    return temp


def parametersValues(self):
    temp  = []
    if( self.current_token[0] == 'id'):
        temp.append( self.current_token)
        self.match('id')
        temp2 = self.fromID()
        if(temp2 is not None):
            temp +=  temp2
    elif(self.current_token[0] in ['caracter', 'entero']):
        temp.append( self.typesValues() )
    else:
        self.error( ['id', 'caracter', 'entero'] )
    return temp

def fromID(self):
    temp = []
    toEpsilon = ['igual_a', 'menor', 'menor_igual', 'mayor', 'mayor_igual', 'diferente', 'mult', 'div_entera', 'MOD', 'suma', 'resta', 'parentesis_c', 'corchete_c', 'punto_coma']
    if(self.current_token[0] == 'corchete_a'):
        temp.append(self.arrayPos() )
    elif(self.current_token[0] == 'punto'):
        temp.append(self.lenght() )
    elif( (self.current_token[0] in toEpsilon) or (self.current_token in [HASTA, PASO])):
        return None
    else:
        predict = toEpsilon + [HASTA, PASO, 'corchete_a', 'punto']
        self.error(predict)
    return temp

def typesValues(self):
    temp = self.current_token
    self.current_token
    if(self.current_token[0] == 'caracter'):
        self.match('caracter')
    elif(self.current_token[0] == 'entero'):
        self.match('entero')
    else:
        self.error(['caracter', 'entero'])
    return self.semantic.getIDValue(temp)

def typesId(self):
    temp = None
    if(self.current_token[0] == 'caracter' or self.current_token[0] == 'entero'):
        temp = self.typesValues()
    elif(self.current_token[0] == 'id'):
        temp = self.current_token
        self.match('id')
    else:
        self.error(['caracter', 'id', 'entero'])
    return self.semantic.getIDValue(temp)
