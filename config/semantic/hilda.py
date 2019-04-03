def buildInFunctions(self, function):
    self.logger.info(f"<Build-inFunction> prototype:\t{function}")
    if( function['name'].lower() == 'escribe' ):
        if( len(function['parameters']) == 1 ):
            to_print = function['parameters'][0]
            to_print = to_print if not 'id' in to_print else to_print['value']
            print( to_print['value'] )
        else:
            error_msg = f"Expected 1 parameter found:\t{len(function['parameters'])}"
            self.error( error_msg )
    elif( function['name'].lower() == 'lee' ):
        if( (len(function['parameters']) > 1) and not ('id' in function['parameters'][0]) ):
            error_msg = "Invalid call to functions <lee>."
            self.error( error_msg )

        const_var = self.symbols_table.getConst( function['parameters'][0]['id'] )
        if(const_var is not None):
            error_msg = f"Can't perform operation over unmutable variable:\t"
            error_msg += f"{function['parameters'][0]['id']}"
            self.error( error_msg )

        var = self.symbols_table.getId( function['parameters'][0]['id'] )
        # Since >const_var< was None it's only necessary check for >var<
        if( var is None ):
            error_msg = f"No previous declaration of variable: {function['parameters'][0]['id']}."
            self.error( error_msg )

        value = input()
        if( value.isdecimal() ):
            value = {'type':'entero', 'value': str(value)}
        elif( value.isalpha() ):
            if( len(value) == 1):
                value = {'type':'caracter', 'value': value}
            else:
                self.error("<Cadenas> are't supported.")
        else:
            error_msg = f"Unknown type:\t{value}."
            self.error( error_msg )

        self.assigment({
                'id': function['parameters'][0]['id'],
                'value': value
            })
    else:
        return False

    return True

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
    self.logger.debug("Getting var. Variable patting:\t"+str(var_path))
    const_var = self.symbols_table.getConst( var_path['id'] )
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
    self.logger.debug("Array operation:\tvar_path:"+str(var_path)+"\tvar:"+str(var))
    array = var['value']['value']
    if('index' in var_path):
        if( var_path['index']['type'] != 'entero' ):
            error_msg = "Index must be >{0}< not <{1}>".format('entero', var_path['index'])
            self.error(error_msg)
        elif( len(array) > int(var_path['index']['value']) ):
            return {
                    'type':var['value']['type'],
                    'value':array[ int(var_path['index']['value']) ]
                    }
        else:
            error_msg = f"Index out of bound for array: {var_path['id']}."
            self.error( error_msg )
    elif('method' in var_path):
        if(var_path['method']['lexeme'] == 'length'):
            return {'type':'entero', 'value':str(len( array ))}
        else:
            error_msg = "Unknown method: {0}.".format(var_path['method'])
            self.error( error_msg )
    else:
        error_msg = "Unknown <ARRAY> operation."
        self.error( error_msg )

def solveExpr(self, expr):
    self.logger.debug("Expression to solve:\t"+str(expr))
    result = {'type':expr['left']['type']}

    if( (expr['left']['type'] == 'entero') and (expr['right']['type'] == 'entero') ):
        if(expr['operator']['lexeme'] == 'MOD'):
            result['value'] =  eval(
                    str(expr['left']['value'])+
                    ' ' +
                    '%'+
                    ' ' +
                    str(expr['right']['value'])
                )
        else:
            result['value'] = eval(
                    str(expr['left']['value'])+
                    ' ' +
                    expr['operator']['lexeme']+
                    ' ' +
                    str(expr['right']['value'])
                )
    else:
        error_msg = "Both operators most be type >entero<. "
        error_msg += "Given: RIGHT:{0},LEFT:{1}".format(expr['right'], expr['left'])
        error_msg += f" At line:{expr['line']}"
        self.error(error_msg)

    if( result['value'] < 0 ):
        error_msg = f"Operation result out of real numbers domain. At line:{expr['line']}"
        self.error( error_msg )

    return result

def resolveCondition(self, condition):
    self.logger.debug("Condition to solve:\t"+str(condition))
    if('id' in condition['left'] ):
        condition['left'] = self.getVarValue( condition['left'] )
    if('id' in condition['right'] ):
        condition['right'] = self.getVarValue( condition['right'] )

    if( condition['left']['type'] == condition['right']['type'] ):
        if( condition['left']['type'] == 'caracter' ):
            condition['left']['value'] = '"'+condition['left']['value']+'"'
            condition['right']['value'] = '"'+condition['right']['value']+'"'
        result = eval(
                str(condition['left']['value'])+
                ' ' +
                condition['operator']['lexeme']+
                ' ' +
                str(condition['right']['value'])
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

    return {'type':type, 'value':final_array}

def constDef(self, var_def):
    if( self.symbols_table.getConst( var_def['id'] ) is None ):
        self.symbols_table.addConst(
            var_def['id'],
            var_def['value']['type'],
            var_def['value']['value']
            )
    else:
        error_msg = "Previous declaration of constant: {0}".format(var_def['id'])
        self.error(error_msg)

def assigment(self, assigment):
    self.logger.info("<ASIGNACION>:Prototype:\t"+str(assigment))
    if(self.symbols_table.getConst(assigment['id']) is not None):
        error_msg = "Unmutable variable: {0}".format( assigment['id'] )
        self.error( error_msg )

    var_found = self.symbols_table.getId( assigment['id'] )
    if( var_found is not None ):
        self.logger.debug("Var found:"+str(var_found))
        type = var_found['type'] if not var_found['type'] == 'array' else var_found['value']['type']
        if( assigment['value']['type'] != type ):
            error_msg = f"Mismatch of variable type with assigmente value."
            error_msg += f"Variable type {var_found['type']} and"
            error_msg += f" assigment value of tye {assigment['value']['type']}."
            self.error( error_msg )
        elif( var_found['type'] == 'array' and 'index' in assigment ):
            self.logger.debug("<ASIGNACION>:Array position.")
            var_found['value']['value'][ int(assigment['index']['value']) ] = assigment['value']['value']
            self.logger.debug(f"<ASIGNACION>:Value assigned={var_found['value']['value'][ int(assigment['index']['value']) ]}")
            return 0

    self.symbols_table.addId(
        assigment['id'],
        assigment['value']['type'],
        assigment['value']['value']
    )

    return 0 if var_found else 1

def paraInit(self, para):
    self.logger.info("<PARA>:Init:\t"+str(para))
    exist = 0
    para['step'] = para['step']['type']+para['step']['value']['value']
    if( 'value' in para['ctrl_var'] ):
        if( para['ctrl_var']['value']['type'] == 'entero'):
            para['ctrl_var']['value']['value'] = str(eval( str(para['ctrl_var']['value']['value'])+'- '+para['step'] ))
            exist = self.assigment( para['ctrl_var'] )
        else:
            error_msg = "Ctrl variable most be type >entero<. Not: {0}".format(para['ctrl_var'])
            self.error(error_msg)

    para['ctrl_var'] = {'id':para['ctrl_var']['id']}

    to_var = para['to'] if not 'id' in para['to'] else para['to']['value']
    if( to_var['type'] != 'entero' ):
        error_msg = "Limit variable most be type >entero<. Not: {0}".format(para['to'])
        self.error(error_msg)

    return exist, para

def paraIter(self, para):
    self.logger.info("<PARA>:Iteration:\t"+str(para))
    var = self.symbols_table.getId( para['ctrl_var']['id'] )
    self.logger.debug("Variable to update:\t"+str(var))

    debug_msg = f"<PARA> limit checking. Current:{var['value']} To:{para['to']}"
    self.logger.debug(debug_msg)

    if( 'id' in para['to'] ):
        to_var = self.getVarValue( para['to'] )['value']
    else:
        to_var = para['to']['value']

    if( int(var['value']) != int(to_var) ):
        var['value'] = str( eval(var['value']+' + '+para['step']) )
        self.symbols_table.addId(
                para['ctrl_var']['id'],
                var['type'],
                var['value']
            )
        return True
    else:
        return False

def init():
    pass

def semantic():
    return [
                'resolveTypeValue',
                'buildInFunctions',
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
