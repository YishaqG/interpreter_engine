def convertArguments(self, args):
    values = []
    for arg in args:
        if(arg[0] == 'entero'):
            values.append(int(arg[1]))
        if(arg[0] == 'id'):
            values.append( arg[1] )

    return values

def initSubSM(self):
    if(self.subSM is None):
        self.subSM = Semantic(self.symbols_table)

def hasSubSM(self):
    return True if self.subSM is not None else False

def defConst(self, inst):
    NAME = 0
    VALUE = 1

    if( self.symbols_table.getCONST( inst[NAME][Lexer.Token.LEXEME.value] ) is None ):
        self.symbols_table.addCONST(
            inst[VALUE][Lexer.Token.TYPE.value],
            inst[NAME][Lexer.Token.LEXEME.value],
            inst[VALUE][Lexer.Token.LEXEME.value]
            )
    else:
        self.error("Already defined constant=%r" %(inst[NAME][Lexer.Token.LEXEME.value]))

def defArray(self, inst):
    NAME = 0
    VALUE = 1
    inst[NAME] = (inst[NAME][Lexer.Token.LEXEME.value].lower(), inst[NAME][Lexer.Token.LEXEME.value])
    if( not self.symbols_table.getID( inst[NAME][Lexer.Token.LEXEME.value] ) ):
        self.symbols_table.addID(
            'array',
            inst[NAME][Lexer.Token.LEXEME.value],
            self.shapeArray(inst[VALUE])
        )
    else:
        self.logger.error("Already defined vaiable=%r"%(inst[NAME][Lexer.Token.LEXEME.value]))
        raise SemanticError

def shapeArray(self, array):
    newArray = []
    type = array[0][0]
    error = False
    for element in array:
        if(element[0] != type):
            error = True
        newArray.append( element[1] )

    if( error ):
        self.logger.error("Conflicting types at array %r" %(array))
        raise SemanticError

    return (type, array)

def function(self, inst):
    #TODO Validar el numero de los parametros porporcionados
    NAME = 0
    VALUE = 1
    if( inst[NAME][Lexer.Token.LEXEME.value] == "ESCRIBE" ):
        idValue = self.getIDValue( inst[VALUE] )
        if(idValue is not None):
            self.logger.info( idValue[VALUE] )
        else:
            self.logger.info( inst[VALUE][Lexer.Token.LEXEME.value] )
    else:
        pass
        # if( inst[VALUE][Lexer.Token.TYPE.value] == 'id' ):
        #     idValue = self.getIDValue( inst[VALUE] )
        #     if(idValue is not None):
        #         input_value = askstring("Input", "Value")
        #         if(input_value is None):
        #             raise SemanticError
        #         if( (idValue[0] == 'caracter') and input_value.isalpha() and len(input_value) == 1 ):
        #             self.symbols_table.addID( idValue[0], id_value[1], input_value  )
        #         elif( (idValue[0] == 'entero') and input_value.isdigit() ):
        #             self.symbols_table.addID( idValue[0], id_value[1], int(input_value)  )
        #         else:
        #             error_msg = "Variable type=%r found %r" %(idValue[0], input_value)
        #             self.logger.error(error_msg)
        #     else:
        #         error_msg = "Not previous declaration of <id> %r" %(inst[VALUE][Lexer.Token.LEXEME.value])
        #         self.logger.error(error_msg)
        # else:
        #     error_msg = "Must be <id> not %r" %(inst[VALUE][Lexer.Token.TYPE.value])
        #     self.logger.error(error_msg)

def getIDValue(self, id):
    # id
    # [id, index] optain value
    idValue = None
    if( id[0][0] != 'id' ):
        return id

    print("id"+str(id))

    idValue = self.symbols_table.getID( id[0][1].lower() )
    if( len(id) == 1 ):
        if(idValue is None):
            idValue = self.symbols_table.getCONST( id[0][1] )
    elif( len(id) == 2 ):
        valIndex = True if id[1][0] == 'entero' else False
        if( valIndex ):
            return idValue[1][1][ id[1][1] ]
        else:
            self.logger.error("Index must be <entero>")
            raise SemanticError

    if( idValue is not None ):
        return idValue
    else:
        error_msg = "Not previous declaration of variable= %r" %(str(id[0]))
        self.logger.error(error_msg)
        raise SemanticError

def updateIDValue(self, inst):
    # [id, value]
    # [id, index, value]
    if( inst[0][0] == 'id' ):
        idValue = self.symbols_table.getCONST( inst[0][1] )
        if(idValue is not None):
            self.logger.error("Constant variables aren't mutable")
            raise SemanticError
    else:
        return id

    if( len(inst) == 2 ):
        idValue = self.getIDValue( inst[0] )
        if( idValue[0] == inst[1][0] ):
            self.symbols_table.addID(idValue[0], inst[0][1], inst[1][1])
        else:
            error_msg = "Value type=%r must be variable's type=%r"%(inst[1][0], idValue[0])
            self.logger.error(error_msg)
            raise SemanticError
    elif( len(id) == 3 ):
        idValue = getIDValue( inst[0] )
        if( idValue[1][0] == inst[2][0] ):
            idValue[1][1][ inst[1][1] ] = inst[2][1]
            self.symbols_table.addID('array', (inst[0][1], idValue))
        else:
            self.logger.error("Value type=%r must be array's type=%r"%(inst[1][0], idValue[0]))
            raise SemanticError

def arrayOperations(self, array_op):
    # (id, lenght)
    # (id, index, val)
    value = getIDValue( array_op[0] )
    if( value[0] != 'array' ):
        self.error("Not an array variable")
        raise SemanticError
    valIndex = True if array_op[1][0] == 'entero' else False
    if( len(array_op) == 2 ):
        if( array_op[1][1] == 'lenght' ):
            return len( value[1][1] )
        else:
            self.error("Unknown operation.")
            raise SemanticError
    elif( len(array_op) == 3 ):
        self.updateIDValue(array_op)
    else:
        self.logger.error("Unknown instruction=%r" %(array_op))
        raise SemanticError

def transitions(self, inst):
    print("Processing instruction:"+str(inst))
    print("current_state:"+str(self.current_state))
    if(self.current_state == 0):
        if( inst[0] == 'PARA' ):
            self.current_state = 2
        elif( inst[0] == 'SI' ):
            self.current_state = 5
        else:
            self.current_state = 1
            self.transitions(inst)
    elif(self.current_state == 1): # INST
        if(inst[0][1] == 'FIN'):
            self.current_state = 4
        else:
            self.inst(inst)
    elif(self.current_state == 2): # PARA
        self.initSubSM()
        self.paraCondition = [inst[0][1], inst[2][1], inst[3][1]]
        self.expr(inst[:2])
        self.current_state = 3
    elif(self.current_state == 3): # PARA_BODY
        self.para(inst)
    elif(self.current_state == 4):
        self.current_state = 0
        self.subSM = None
        return True # It has finished
    elif(self.current_state == 5): # SI_CONDITION
        self.logger.info("Checking <SI> condition")
        self.initSubSM()
        print(eval("%r%s%r"%(inst[0][1], inst[1][1], inst[2][1])))
        if( eval("%r%s%r"%(inst[0][1], inst[1][1], inst[2][1])) ):
            self.current_state = 6
        else:
            self.current_state = 7
    elif(self.current_state == 6): # SI_BODY
        self.logger.info("Processing <SI> body")
        if( self.subSM.transitions(inst) or ( (not self.subSM.hasSubSM()) and inst[0] == 'NOSI') ):
            self.current_state = 8
    elif(self.current_state == 7): # SI_IGNORE
        self.logger.info("Ignoring <SI> body")
        if( inst[0] == 'NOSI' ):
            self.current_state = 9
    elif(self.current_state == 8): # NOSI_IGNORE
        self.logger.info("Ingnoring <NOSI> body")
        if( inst[0] == 'FIN' ):
            self.current_state = 4
            self.transitions(inst)
    elif(self.current_state == 9): # NOSI_BODY
        self.logger.info("Processing <NOSI> body")
        if( self.subSM.transitions(inst) or ( (not self.subSM.hasSubSM()) and inst[0] == 'FIN') ):
            self.current_state = 4
            self.transitions(inst)
    elif(self.current_state == 10):
        if( self.subSM.transitions(inst) or ( (not self.subSM.hasSubSM()) and inst[0] == 'FIN') ):
            self.current_state = 4
            self.transitions(inst)

    return False # It has not finished

def inst(self, inst):
    if( inst[0][0] == 'function' ):
        self.function(inst)
    elif( inst[0] == 'PARA' ):
        self.current_state = 2
    elif( inst[0] == 'SI' ):
        self.current_state = 5
    else:
        self.current_state = 1

def expr(self, inst):
    if(self.current_state in [8,9]):
        return None
    # 1: i=<parametersValues> [id, value]
    # 1.1: i[x]=<parametersValues>  [id, index, value]
    # 2: a<operador>b
    self.logger.debug("Expr = "+str(inst))
    if( inst[0][0] == 'id' ):
        idValue = self.symbols_table.checkID(inst[0])
        if( idValue ):
            self.updateIDValue(inst)
        else:
            self.symbols_table.addID(inst[1][0], inst[0][1].lower(), inst[1][1])
    else:
        return eval("%r%s%r"%(inst[0][1], inst[1][1], inst[1][1]))

def para(self, inst): # (varCtrl, varCtrlVal, limite, paso)
    ctrlVar = self.getIDValue( self.para[0] )
    if( (ctrlVar[1] == self.paraCondition[1]) and (inst[0] == 'FIN') ):
        self.current_token = 4
        self.transitions(inst)
    elif( self.subSM.transitions(inst) or ( (not self.subSM.hasSubSM()) and inst[0] == 'NOSI') ):
        if( self.subSM.transitions(inst) ):
            self.current_state = 3
            self.transitions(inst)
