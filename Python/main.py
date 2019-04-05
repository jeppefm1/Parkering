import cv2
import numpy as np
import os

import findChars
import findPlates
import classPossiblePlate

IMAGE =  "6.png"

COLOR_BLACK = (0.0, 0.0, 0.0)
COLOR_WHITE = (255.0, 255.0, 255.0)
COLOR_YELLOW = (0.0, 255.0, 255.0)
COLOR_GREEN = (0.0, 255.0, 0.0)
COLOR_RED = (0.0, 0.0, 255.0)


def main():
    #Indlæs billede
    image  = cv2.imread(IMAGE)

    #Anvend egne funktioner til at finde mulige nummerplader og chars
    listOfPossiblePlates = findPlates.findPlatesInImg(image)
    listOfPossiblePlates = findChars.detectCharsInPlates(listOfPossiblePlates)

    #Vis billede
    cv2.imshow("Billede", image)

    #Check om der blev fundet nummerplaer
    if len(listOfPossiblePlates) == 0:
        print("\nno license plates were detected\n")
    else:
        #Sorter mulige nummerplader efter længde. Her kommer den længste nummerplade først.
        #Til sorteringen anvendes en lamda funktion, der finder længden af nummerpladen
        listOfPossiblePlates.sort(key = lambda possiblePlate: len(possiblePlate.charsInPlate), reverse = True)

        #Antag at den længste nummerplade er den korrekte
        licPlate = listOfPossiblePlates[0]
        #Vis nummerpladen og thresshold billedet
        cv2.imshow("imgPlate", licPlate.imgPlate)
        cv2.imshow("imgThresh", licPlate.imgThressholded)

        #Hvis ingen chars er genkendt
        if len(licPlate.charsInPlate) == 0:
            print("\nno characters were detected\n\n")
            return

        #Tegn regtangel omkring nummerplade
        drawRedRectangleAroundPlate(image, licPlate)
        #Print nummerpladen
        print("\nlicense plate read from image = " + licPlate.charsInPlate + "\n")  # write license plate text to std out
        print("----------------------------------------")

        #Vis nummerpladen på billedet
        writeLicensePlateCharsOnImage(image, licPlate)
        cv2.imshow("Nummerplade genkendt", image)
        #Gem billedet
        cv2.imwrite("nummerpladeGenkendt.png", image)
        cv2.waitKey(0)
        return

#Funktion til at tegne rød regtangel omkring nummerpladen
def drawRedRectangleAroundPlate(imgOriginalScene, licPlate):
    centerOfTextAreaX = 0
    centerOfTextAreaY = 0
    lowerLeftTextOriginX = 0
    lowerLeftTextOriginY = 0
    #Find punkter
    rectPoints = cv2.boxPoints(licPlate.locationInImg)
    cv2.line(imgOriginalScene, tuple(rectPoints[0]), tuple(rectPoints[1]), COLOR_RED, 2)
    cv2.line(imgOriginalScene, tuple(rectPoints[1]), tuple(rectPoints[2]), COLOR_RED, 2)
    cv2.line(imgOriginalScene, tuple(rectPoints[2]), tuple(rectPoints[3]), COLOR_RED, 2)
    cv2.line(imgOriginalScene, tuple(rectPoints[3]), tuple(rectPoints[0]), COLOR_RED, 2)

def writeLicensePlateCharsOnImage(image, licPlate):
    #Henter oplysninger om billedet
    sceneHeight, sceneWidth, sceneNumChannels = image.shape
    plateHeight, plateWidth, plateNumChannels = licPlate.imgPlate.shape

    #Instillinger omkring skrifttype og størrelse
    fontFace = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = float(plateHeight) / 30.0
    fontThickness = int(round(fontScale * 1.5))
    textSize, baseline = cv2.getTextSize(licPlate.charsInPlate, fontFace, fontScale, fontThickness)

    #Hent oplysninger om position i billedet
    ((plateCenterX, plateCenterY), (plateWidth, plateHeight), correctionAngleInDeg) = licPlate.locationInImg
    #Konverter til integer
    plateCenterX = int(plateCenterX)
    plateCenterY = int(plateCenterY)
    centerOfTextAreaX = int(plateCenterX)

    #Bestem om teksten skal være under eller over nummerpladen
    if plateCenterY < (sceneHeight * 0.75):
        centerOfTextAreaY = int(round(plateCenterY)) + int(round(plateHeight * 1.6))
    else:
        centerOfTextAreaY = int(round(plateCenterY)) - int(round(plateHeight * 1.6))

    textSizeWidth, textSizeHeight = textSize
    lowerLeftTextOriginX = int(centerOfTextAreaX - (textSizeWidth / 2))
    lowerLeftTextOriginY = int(centerOfTextAreaY + (textSizeHeight / 2))
    #Tegn tekst på billedet
    cv2.putText(image, licPlate.charsInPlate, (lowerLeftTextOriginX, lowerLeftTextOriginY), fontFace, fontScale, COLOR_YELLOW, fontThickness)

if __name__ == "__main__":
    main()
