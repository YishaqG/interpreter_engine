
def validateStructure(keys, data, msg):
    for key in keys:
        if( key not in data ):
            error_msg = "Unable to load {0} from {1}".format( msg, data )
            raise Exception(error_msg)
