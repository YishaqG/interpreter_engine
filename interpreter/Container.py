

class Container:
    def __init__(self, text):
        self.row_index = 0
        self.column_index = -1
        self.error_count = 0
        self.text = text.splitlines(True)

    def setCoordinates(self, row=None, column=None):
        if(row is not None):
            self.row_index = row

        if(colum is not None):
            self.column_index = column

    def getRow(self):
        return self.text[self.row_index]

    def nextRow(self):
        if( self.row_index < len(self.text)-1 ):
            self.column_index = 0
            self.row_index += 1
            return self.getRow()
        else:
            raise EndOfFileException()

    def prevRow(self):
        if( self.row_index > 0 ):
            self.column_index = self.getCharsInLine()
            self.row_index -= 1
            return self.getRow()
        else:
            return None

    def getChar(self):
        if( self.column_index == -1 ):
            self.column_index = 0

        return self.text[self.row_index][self.column_index]

    def nextChar(self):
        if( self.column_index < self.getCharsInLine() ):
            self.column_index += 1
            return self.getChar()
        elif( self.nextRow() is not None ):
            return self.getChar()
        else:
            raise EndOfFileException()

    def getCharsInLine(self):
        return len(self.text[self.row_index])-1

    def recoilChar(self, recoil):
        if( (self.column_index+1) >= recoil ):
            self.column_index -= recoil
        else:
            recoil -= self.column_index+1
            if( self.prevRow() is not None ):
                self.column_index -= recoil
            else:
                self.column_index = 0

    def getRowIndex(self):
        return self.row_index

    def getColumIndex(self):
        return self.column_index

    def addError(self):
        self.error_count += 1

    def getErrorCount(self):
        return self.error_count

    def getCoordinates(self):
        return "%d:%d" % (self.getRowIndex(), self.getColumIndex())

    def numberOfRows(self):
        return len( self.text )

class EndOfFileException(Exception):
    def __init__(self):
        pass
