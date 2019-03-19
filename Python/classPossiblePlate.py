import cv2
import numpy as np

#Klasse der kan gemme potentielle nummerplader
#Her gemmes billedet at nummerpladen i tre udgaver, original, grayscale og thressholdet
#Derudover gemmes lokationen i billedet, samt de læste bogstaver eller tal i nummerpladen.

class PossiblePlate:
    def __init__(self):
        #variabler til billederne
        self.imgPlate = None
        self.imgGrayscaled = None
        self.imgThressholded = None
        #Position i billedet
        self.locationInImg = None
        #Mulige bogstaver eller tal
        self.charsInPlate = ""
