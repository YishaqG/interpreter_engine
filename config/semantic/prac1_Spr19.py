import tkinter as tk
import time, math
from PIL import ImageTk, Image

class FacesBox( tk.Canvas ):

    def __init__(self, master):
        self.width = 800
        self.height = 800
        self.objects = []
        super().__init__(master, width=self.width, height=self.height, background="white", highlightthickness=0)

    def __exist(self, tag):
        if( len( self.find_withtag(tag) ) == 0 ):
            return None

        return "Tag with name: {0} already exist".format(tag)

    def __validCoordinates(self, x, y):
        if( x > 0 and x <= self.width ):
            if( y > 0 and y <= self.height ):
                return None

        return "Node out of bound maxWidth={0}, maxHeight={1}".format(self.width, self.height)

    def __validSize(self, x, y, radio):
        if( x-radio >= 0 and x+radio <= self.width ):
            if( y-radio >= 0 and y+radio <= self.height ):
                return None

        return "Drawing out of bound maxWidth={0}, maxHeight={1}".format(self.width, self.height)

    def __validMode(self, mode):
        modes = ['feliz', 'dormida', 'enojada', 'triste', 'neutral']
        if( mode in modes ):
            return None

        return "Invalid mode: {0}. Valid modes: {1}".format(mode, ['feliz', 'dormido', 'enojado', 'triste', 'neutral'])

    def __validArguments(self, coords=None, radio=None, name=None, mode=None):
        if(name is not None):
            valid = self.__exist(name)
            if( valid is not None ):
                return valid

        if(coords is not None):
            valid = self.__validCoordinates(coords[0], coords[1])
            if( valid is not None ):
                return valid

        if(radio is not None):
            valid = self.__validSize(coords[0], coords[1], radio)
            if( valid is not None ):
                return valid

        if(mode is not None):
            valid = self.__validMode(mode)
            if( valid is not None ):
                return valid

    def DibujarCara(self, x, y, radio, name, mode):

        valid = self.__validArguments((x,y), radio, name, mode)
        if( valid is not None ):
            return valid

        diameter = int(radio*2)
        img = Image.open("config/assets/prac1_Spr19/"+mode+".png")
        img = img.resize( (diameter,diameter), Image.ANTIALIAS)

        imgTk = ImageTk.PhotoImage(img)
        self.objects.append(imgTk)
        print(self.objects)
        self.create_image( x, y, image=imgTk, tag=name)

        self.create_text(x,y,text=name, tag=(name+"_text"))
        self.update()

    def CambiarModo(self, name, mode):

        valid = self.__validArguments(name=name)
        if( valid is not None ):
            valid = self.__validArguments(mode=mode)
            if( valid is not None ):
                return valid
            (imgCoords) = self.bbox( name )
            x = int( (imgCoords[0]+imgCoords[2])/2 )
            y = int( (imgCoords[1]+imgCoords[3])/2 )
            radio = int( math.sqrt( ((imgCoords[0]-imgCoords[2])**2)+((imgCoords[1]-imgCoords[3])**2)) )
            self.EliminarCara(name)
            self.DibujarCara( x, y, radio, name, mode)
        else:
            return "Tag with name: {0} doesn't exist".format(name)

    def EliminarCara(self, name):
        valid = self.__validArguments(name=name)
        if( valid is not None ):
            self.delete(name)
            self.delete(name+"_text")
            self.update()
        else:
            return "Tag with name: {0} doesn't exist".format(name)

    def Dormir(self, sec):
        time.sleep(sec)


def init():
    sub_window = tk.Toplevel(  )
    faces = FacesBox(sub_window)
    faces.pack()
    return faces

def semantic():
    pass
