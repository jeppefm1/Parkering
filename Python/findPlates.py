import cv2
import numpy as np
import math
import random

import numberplateRec
import imageProcess
import findChars
import classPossiblePlate
import classPossibleChar

#Konstanter der beskriver nummerplades kendetegn
PLATE_WIDTH_PADDING_FACTOR = 1.3
PLATE_HEIGHT_PADDING_FACTOR = 1.5

def findPlatesInImg(imgCaptured):
    #Tom liste til at gemme mulige nummerplader
    listOfPossiblePlates = []
    #Finder billedets dimmensioner
    height, width, numChannels = imgCaptured.shape

    #Laver tomme arrays til billeder og konturer
    imgGrayscaleScene = np.zeros((height, width, 1), np.uint8)
    imgThreshScene = np.zeros((height, width, 1), np.uint8)
    imgContours = np.zeros((height, width, 3), np.uint8)

    #Anvender egen funktion til at grayscale og thessholde billedet
    imgGrayscaleScene, imgThreshScene = imageProcess.preprocessImg(imgCaptured)
    #Anvender egen funktion til at finde mulige bogstaver og tal i billedet
    listOfPossibleCharsInScene = findPotentialCharsInIMG(imgThreshScene)

    #Anvender liste med alle potentielle bogstaver eller tal til at grupperer dem efter andre der ligner dem.
    listOfListsOfMatchingCharsInScene = findChars.findListOfListsOfMatchingChars(listOfPossibleCharsInScene)
    #Herefter bliver der prøvet at genkende en nummerplade ud fra hver gruppe.
    for listOfMatchingChars in listOfListsOfMatchingCharsInScene:
        possiblePlate = extractPlate(imgCaptured, listOfMatchingChars)
        #Gemmer de potentielle nummerplader i liste
        if possiblePlate.imgPlate is not None:
            listOfPossiblePlates.append(possiblePlate)
    #Print antallet af fundne nummerplader
    print("\n" + str(len(listOfPossiblePlates)) + " mulige nummerplader fundet")
    return listOfPossiblePlates


def findPotentialCharsInIMG(imgThresh):
    #Laver liste til at gemme chars, samt en variabel til at tælle antallet af chars
    listOfPossibleChars = []
    countOfPossibleChars = 0
    #Kopirer billedet, da søgningen vil ændre i det.
    imgThreshCopy = imgThresh.copy()

    #Anvender Cv2 til at finde konturer i billedet
    contours, npaHierarchy = cv2.findContours(imgThreshCopy, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #Laver et tomt array til konturerne
    height, width = imgThresh.shape
    imgContours = np.zeros((height, width, 3), np.uint8)

    #Loop gennem konturer
    for i in range(0, len(contours)):
        #Laver et nyt objekt til at gemme det potentielle char
        possibleChar = classPossibleChar.PossibleChar(contours[i])

        #Hvis konturen opfylder reglerne for en char, gemmes objektet i en liste.
        if findChars.checkIfPossibleChar(possibleChar):
            countOfPossibleChars = countOfPossibleChars + 1
            listOfPossibleChars.append(possibleChar)

    return listOfPossibleChars


def extractPlate(imgCaptured, listOfMatchingChars):
    #Lav nummerplade objekt
    possiblePlate = classPossiblePlate.PossiblePlate()

    #Sorter fundende bogstaver efter x position. Listen går dermed fra venstre mod højre.
    #lamda keywordet kan bruges til at definere en funktion i python.
    #I dette tilfælde betyder det, at key bliver sat til x værdien, og det er dermed den der anvendes til sorteringen.
    listOfMatchingChars.sort(key = lambda matchingChar: matchingChar.centerX)

    #Find centerpunket i nummerpladen
    plateCenterX = (listOfMatchingChars[0].centerX + listOfMatchingChars[len(listOfMatchingChars) - 1].centerX) / 2.0
    plateCenterY = (listOfMatchingChars[0].centerY + listOfMatchingChars[len(listOfMatchingChars) - 1].centerY) / 2.0
    #Gem centrum i en tuple
    plateCenter = plateCenterX, plateCenterY

    #Bestem nummerpladens dimmensioner - hermed højde og bredde.
    #Bredden bestemmes ved at finde x hjørnepunktet. Derefter anvendes bredden til at finde det andet hjørnepunkt.
    #Derefter anvendes bredde konstanten til at trække kanten fra.
    plateWidth = int((listOfMatchingChars[len(listOfMatchingChars) - 1].boundingRectX + listOfMatchingChars[len(listOfMatchingChars) - 1].boundingRectWidth - listOfMatchingChars[0].boundingRectX) * PLATE_WIDTH_PADDING_FACTOR)

    #Højden af nummerpladen findes derefter som et gennemsnit af alle bogstavernes højde.
    #Også her anvendes en konstant til at korrigere nummerpladens højde.
    totalCharHeights = 0

    for matchingChar in listOfMatchingChars:
        totalCharHeights = totalCharHeights + matchingChar.boundingRectHeight

    averageCharHeight = totalCharHeights / len(listOfMatchingChars)
    plateHeight = int(averageCharHeight * PLATE_HEIGHT_PADDING_FACTOR)

    #Bestemmer derfor den vinkel som nummerpladen er drejet med.
    #Hertil anvendes sinus relationen.
    opposite = listOfMatchingChars[len(listOfMatchingChars) - 1].centerY - listOfMatchingChars[0].centerY
    hypotenuse = findChars.distanceBetweenCharsFunction(listOfMatchingChars[0], listOfMatchingChars[len(listOfMatchingChars) - 1])
    correctionAngleRad = math.asin(opposite / hypotenuse)
    correctionAngleDeg = correctionAngleRad * (180.0 / math.pi)

    #Gemmer oplysninger i klassen
    possiblePlate.locationInImg = (tuple(plateCenter), (plateWidth, plateHeight), correctionAngleDeg)

    #Opretter derefter en rotationsmatrix til at rotere nummerpladen.
    #Hertil anvendes den beregnede vinkel.
    #Syntax: cv2.getRotationMatrix2D(center, angle, scale)
    rotationMatrix = cv2.getRotationMatrix2D(tuple(plateCenter), correctionAngleDeg, 1.0)

    #Den oprettede matrix kan derefter anvendes til at roterer hele billedet
    #Her skal billedets oplysninger bruges.
    height, width, numChannels = imgCaptured.shape
    imgRotated = cv2.warpAffine(imgCaptured, rotationMatrix, (width, height))

    #Beskærer billedet således at det kun er nummerpladen
    imgCropped = cv2.getRectSubPix(imgRotated, (plateWidth, plateHeight), tuple(plateCenter))
    #Gemmer nummerpladen i klassen.
    possiblePlate.imgPlate = imgCropped
    #Returnerer klassen
    return possiblePlate
