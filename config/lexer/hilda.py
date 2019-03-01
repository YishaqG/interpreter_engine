def extension():
    return {
        'functions': [
                'getCharacter'
            ],
        'types': [
                'caracter'
            ]
    }

def builtInTypesExtension(self, current_char):
    lexeme = None
    evaluation = None
    if(current_char == '\''):
        lexeme = self.getCaracter()
        evaluation = 'caracter'

    return evaluation, lexeme

def getCaracter(self):
    current_char = self.source.nextChar()

    if(self.source.nextChar() != '\''):
        error_msg = "Invalid sequence found at {0}\n".format(
            self.source.getCoordinates()
            )
        self.error(error_msg)

    return current_char
