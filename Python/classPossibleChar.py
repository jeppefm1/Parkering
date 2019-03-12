import cv2
import numpy as np
import math

#Klasse der kan gemme potentielle bogstaver eller tal i nummerpladen
#Her gemmes kontouren, dens position, størrelse samt højde bredde forhold.

class PossibleChar:
    def __init__ (self, _contour):
        #Kontour billede der bliver venlagt i oprettelsen af objektet
        self.contour = _contour
        #Bestemmer position og størrelse
        self.boundingRect = cv2.boundingRect(self.contour)
        [x, y, w, h] = self.boundingRect
        #Gemmer i individuelle variabler
        self.boundingRectX = x
        self.boundingRectY = y
        self.boundingRectWidth = w
        self.boundingRectHeight = h

        #Bestemmer arealet af konturen.
        self.boundingRectArea = self.boundingRectWidth * self.boundingRectHeight
        #Finder center koordinater
        self.centerX = (self.boundingRectX + self.boundingRectX + self.boundingRectWidth) / 2
        self.centerY = (self.boundingRectY + self.boundingRectY + self.boundingRectHeight) / 2

        #Beregner diagonal længde ved hjælp af pytagoras
        self.diagonalSize = math.sqrt((self.boundingRectWidth ** 2) + (self.boundingRectHeight ** 2))
        #Beregner højde bredde forhold, da dette kan anvendes til at bestemme om konturen er et bogstav.
        self.aspectRatio = float(self.boundingRectWidth) / float(self.boundingRectHeight)
