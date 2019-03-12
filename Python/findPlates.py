import cv2
import numpy as np
import math
import random

import main
import imageProcess
import findChars
import classPossiblePlate
import classPossibleChar

def findPlatesInImg(imgCaptured):
    #Tom liste til at gemme mulige nummerplader
    listOfPossiblePlates = []
    #Finder billedets dimmensioner
    height, width, numChannels = imgOriginalScene.shape

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
    print("\n" + str(len(listOfPossiblePlates)) + " possible plates found")
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
            countOfPossibleChars = intCountOfPossibleChars + 1
            listOfPossibleChars.append(possibleChar)

    return listOfPossibleChars


def extractPlate(imgCaptured, listOfMatchingChars):
    return possiblePlate
