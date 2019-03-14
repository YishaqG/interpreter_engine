import logging, re, types, sys, functools
from importlib import util
from pathlib import Path

def semantic_status(func, *, disable=False):
    @functools.wraps(func)
    def wraper(*args, **kwargs):
        if( not disable ):
            return func(*args, **kwargs)


    return wraper

class Semantic:
    def __init__(self, symbols_table):
        self.logger = logging.getLogger("Semantic")
        self.symbols_table = symbols_table
        self.source = None
        self.engine = None
        self.stand_by = False

    def error(self, error_msg):
        error_msg = "Semantic:ERROR:" + error_msg
        print( error_msg )
        raise SemanticError

    def setSemantic(self, path):
        self.logger.info("Loading semantic analizer...")
        self.engine = None

        try:
            path = Path(path).resolve()
            self.source = path
            spec = util.spec_from_file_location(path.name, path)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as ex:
            self.logger.error( str(ex) )
            self.error("Unable to load semantic.")

        if( 'semantic' in list(module.__dict__.keys()) ):
            functions = getattr(module, 'semantic')()
            if( functions ):
                self.logger.debug("Semantic:\t"+str(functions) )
                for function in functions:
                    setattr(
                                self,
                                function,
                                semantic_status(
                                        types.MethodType(
                                                getattr(module, function),
                                                self
                                            ),
                                        disable=self.stand_by
                                    )
                            )
        else:
            error_msg = "Define the function >semantic< at your semantic implementation."
            self.error( error_msg )

        self.logger.info('Loaded semantic analizer...')

    def initEngine(self):
        if( self.engine is not None ):
            return None

        self.logger.info("Initializing engine...")
        try:
            path = Path(self.source).resolve()
            spec = util.spec_from_file_location(path.name, path)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as ex:
            self.logger.error(str(ex))
            self.error("Unable to initializing engine.")

        if( 'init' in list(module.__dict__.keys()) ):
            self.engine = getattr(module, "init")()
        else:
            error_msg = "Define the function >init< at your semantic implementation."
            self.error(error_msg)

    def analyze(self, function):
        self.initEngine()
        if( self.stand_by ):
            self.logger.info("Standing By...")
            return None

        func_parameter_types = [x[0] for x in function['parameters']]
        func_parameter_values = self.convertArguments( function['parameters'] )
        if(function['type'] == 'function'):
            self.validArguments(
                                self.symbols_table.getFunctionParameters(function['name']),
                                func_parameter_types
                                )

        try:
            return getattr( self.engine, function['name'] )( *func_parameter_values )
        except SemanticError as ex:
            self.logger.error(str(ex))

    def validArguments(self, expected_args, resived_args):
        if( len(expected_args) != len(resived_args) ):
            error_msg = f"Expecting arguments: {expected_args}. Found: {resived_args}."
            self.error(error_msg)

        for index, arg in enumerate(expected_args):
            if(arg != resived_args[index]):
                error_msg = f"Expecting argument type: {arg}. Found: {resived_args[index]}."
                self.error(error_msg)

class SemanticError(Exception):
    def __init__(self):
        pass
