def resolveTypeValue(self, token):
    self.logger.info('resolveTypeValue')
    if(token['type'] == 'entero'):
        return int(token['lexeme'])
    elif(token['type'] == 'caracter'):
        return token['lexeme']
    else:
        error_msg = "Unknown type: {0}".format( token )
        self.error(error_msg)

def getVarValue(self, var_path):
    self.logger.info("getVarValue")
    const_var = self.symbols_table.getCONST( var_path['id'] )
    if(const_var is not None):
        return const_var

    var = self.symbols_table.getId( var_path['id'] )
    # Since >const_var< was None it's only necessary check for >var<
    if( var is None ):
        error_msg = "No previous declaration of variable: {0}.".format(var_path['id'])
        self.error(error_msg)

    if(var['type'] == 'array'):
        return self.arrayOperation(var_path, var)
    else:
        return var

def arrayOperation(self, var_path, var):
    array = var['value']['value']
    if('index' in var_path):
        if( var_path['index']['type'] != 'entero' ):
            error_msg = "Index must be >{0}< not <{1}>".format('entero', var_path['index'])
            self.error(error_msg)
        elif( len(array) >= var_path['index'] ):
            return {
                    'type':var['value']['type'],
                    'value':array[ int(var_path['index']['value']) ]
                    }
        else:
            error_msg = "Index out of bound."
            self.error( error_msg )
    elif('method' in var_path):
        if(var_path['method'] == 'length'):
            return {'type':'entero', 'value':str(len( array ))}
        else:
            error_msg = "Unknown method: {0}.".format(var_path['method'])
            self.error( error_msg )

def solveExpr(self, expr):
    self.logger.info(resolveExpr)
    self.logger.debug(expr)
    if( (expr['left']['type'] == 'entero') and (expr['right']['type'] == 'entero') ):
        if(expr['operator']['lexeme'] == 'MOD'):
            return eval(
                    expr['left']['value']+
                    ' ' +
                    '%'+
                    ' ' +
                    expr['right']['value']
                )
        else:
            return eval(
                    expr['left']['value']+
                    ' ' +
                    expr['operator']['lexeme']+
                    ' ' +
                    expr['right']['value']
                )
    else:
        error_msg = "Both operators most be type >entero<. "
        error_msg += "Given: RIGHT:{0},LEFT:{1}".format(expr['right'], expr['left'])
        self.error(error_msg)

def resolveCondition(self, condition):
    if( condition['left']['type'] == condition['right']['type'] ):
        result = eval(
                condition['left']['value']+
                ' ' +
                condition['operator']['lexeme']+
                ' ' +
                condition['right']['value']
            )
        if('negate' in condition):
            return eval('not '+str(result))
        else:
            return result
    else:
        error_msg = "Both operators most be the same type. "
        error_msg += "Given: RIGHT:{0},LEFT:{1}".format(expr['right'], expr['left'])
        self.error(error_msg)

def arrayDef(self, var_def):
    if( self.symbols_table.getId( var_def['id'] ) is None ):
        self.symbols_table.addId(
            var_def['id'],
            'array',
            self.shapeArray(var_def['value'])
            )
    else:
        error_msg = "Previous declaration of array: {0}".format(var_def['id'])
        self.error(error_msg)

def shapeArray(self, array):
    final_array = []
    type = array[0]['type']
    error = False
    for element in array:
        if( element['type'] != type ):
            error_msg = "Conflicting types in array: {0}.".format(array)
            self.error(error_msg)
        final_array.append( element['value'] )

    return [type, final_array]

def constDef(self, var_def):
    if( self.symbols_table.getCONST( var_def['id'] ) is None ):
        self.symbols_table.addCONST(
            var_def['id'],
            var_def['value']['type'],
            var_def['value']['value']
            )
    else:
        error_msg = "Previous declaration of constant: {0}".format(var_def['id'])
        self.error(error_msg)

def assigment(self, assigment):
    if(selg.symbols_table.getCONST(assigment['var_access']['id']) is not None):
        error_msg = "Unmutable variable: {0}".format( assigment['var_access']['id'] )
        self.error( error_msg )

    if( selg.symbols_table.getId(assigment['id'])['type'] == 'array' ):
        error_msg = "Unable to perform assigment over >arreglo<."
        self.error(error_msg)

    exist = False
    if(self.symbols_table.getId(assigment['var_access']['id']) is not None):
        exist = True

    self.symbols_table.addId(
            assigment['id'],
            assigment['value']['type'],
            assigment['value']['value']
        )

    return 1 if exist else 0

def paraInit(self, para):
    para['ctrl_var']
    exist = 0
    if( 'value' in para['ctrl_var'] ):
        if( para['ctrl_var']['type'] == 'entero'):
            exist = self.assigment( para['ctrl_var'] )
        else:
            error_msg = "Ctrl variable most be type >entero<. Not: {0}".format(para['ctrl_var'])
            self.error(error_msg)

    para['ctrl_var'] = {'id':para['ctrl_var']['id']}

    if( para['to']['type'] != 'entero' ):
        error_msg = "Limit variable most be type >entero<. Not: {0}".format(para['to'])
        self.error(error_msg)
    para['to'] = para['to']['value']

    para['step'] = para['step']['type']+para['step']['value']

    return exist, para

def paraIter(self, para):
    var = self.symbols_table.getId( para['ctrl_var']['id'] )

    var['value']['value'] = str( eval(var['value']['value']+' + '+para['step']) )
    self.symbols_table.addId(
            var['id'],
            var['value']['type'],
            var['value']['value']
        )

    if( int(var['value']['value']) <= int(para['to']) ):
        return True
    else:
        return False

class BuiltInFunctions:
    pass

def init():
    pass

def semantic():
    return [
                'resolveTypeValue',
                'getVarValue',
                'arrayOperation',
                'solveExpr',
                'resolveCondition',
                'arrayDef',
                'shapeArray',
                'constDef',
                'assigment',
                'paraInit',
                'paraIter'
            ]