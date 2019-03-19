import os
import cv2
import numpy as np
import math
import random

import main
import imageProcess
import classPossibleChar

#Konstanter til at chekke et bogstav eller tal.
#Disse definerer dermed hvordan et char ser ud.
MIN_PIXEL_HEIGHT = 8
MIN_ASPECT_RATIO = 0.25
MAX_ASPECT_RATIO = 1.0
MIN_PIXEL_AREA = 80

#Konstanter til sammenligning af to chars
MIN_DIAG_SIZE_MULTIPLE_AWAY = 0.3
MAX_DIAG_SIZE_MULTIPLE_AWAY = 5.0
MAX_CHANGE_IN_AREA = 0.5
MAX_CHANGE_IN_WIDTH = 0.8
MAX_CHANGE_IN_HEIGHT = 0.2
MAX_ANGLE_BETWEEN_CHARS = 12.0

#Andre konstanter
MIN_NUMBER_OF_MATCHING_CHARS = 3
RESIZED_CHAR_IMAGE_WIDTH = 20
RESIZED_CHAR_IMAGE_HEIGHT = 30
MIN_CONTOUR_AREA = 100

svmModel = cv2.ml.SVM_create()

#Funktion til at loade modellen
def loadModel():
    try:
        svmModel = cv2.ml.SVM_load("SVMmodel.xml")
        return True
    except:
        print("Modellen kunne ikke åbnes. Har du trænet modellen inden?\n")
        os.system("pause")
        return False

def detectCharsInPlates(listOfPossiblePlates):
    #Chekker om der er mulige nummerplader. Hvis ikke spring resten over.
    if len(listOfPossiblePlates) == 0:
        return listOfPossiblePlates

    #Loop for hver nummerplade
    for possiblePlate in listOfPossiblePlates:
        #Grayscale og thresshold mulig nummerplade
        possiblePlate.imgGrayscaled, possiblePlate.imgThressholded = imageProcess.preprocessImg(possiblePlate.imgPlate)

        #Forstør billedet for at nemmere at kunne finde chars
        possiblePlate.imgThressholded = cv2.resize(possiblePlate.imgThressholded, (0, 0), fx = 1.6, fy = 1.6)
        #Thresshold billede igen.
        thresholdValue, possiblePlate.imgThressholded = cv2.threshold(possiblePlate.imgThressholded, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        #Find alle mulige chars i nummerpladen
        #Finder alle konturer, og chekker ud fra konstanterne om det kan være mulige chars.
        listOfPossibleCharsInPlate = findPossibleCharsInPlate(possiblePlate.imgGrayscaled, possiblePlate.imgThressholded)

        #Finder grupper af matchende chars
        listOfListsOfMatchingCharsInPlate = findListOfListsOfMatchingChars(listOfPossibleCharsInPlate)

        #Hvis der ikke blev fundet nogle grupper, må det ikke være en nummerplade.
        if (len(listOfListsOfMatchingCharsInPlate) == 0):
            #Springer dermed videre til næste nummerplade, og gemmer at denne var tom.
            possiblePlate.charsInPlate = ""
            continue

        #Hvis der er mere end en gruppe:
        for i in range(0, len(listOfListsOfMatchingCharsInPlate)):
            #Sorter listen efter center possion. Fra venstre mod højre.
            #Anvender en lamda funktion, der tager center positionen, som nøgle til sorteringen.
            listOfListsOfMatchingCharsInPlate[i].sort(key = lambda matchingChar: matchingChar.intCenterX)
            #Anvender egen funktion til at fjerne overlap mellem bogstaver
            listOfListsOfMatchingCharsInPlate[i] = removeInnerOverlappingChars(listOfListsOfMatchingCharsInPlate[i])

        #Antager at gruppen med flest bogstaver må være den korrekte nummerplade.
        #Kan dermed sortere de andre nummerplader fra.
        lenOfLongestListOfChars = 0
        indexOfLongestListOfChars = 0
        #Anvender et loop til at finde placeringen af den korrekte nummerplade.
        for i in range(0, len(listOfListsOfMatchingCharsInPlate)):
            if len(listOfListsOfMatchingCharsInPlate[i]) > lenOfLongestListOfChars:
                lenOfLongestListOfChars = len(listOfListsOfMatchingCharsInPlate[i])
                indexOfLongestListOfChars = i

        longestListOfMatchingCharsInPlate = listOfListsOfMatchingCharsInPlate[indexOfLongestListOfChars]

        #Anvend egen funktion til klassificeringen af de forskellige chars.
        possiblePlate.charsInPlate = recognizeCharsInPlate(possiblePlate.imgThressholded, longestListOfMatchingCharsInPlate)

    return listOfPossiblePlates

def findPossibleCharsInPlate(imgGrayscaled, imgThressholded):
    listOfPossibleChars = []
    contours = []
    #Nødvendigt med en kopi, da kontur søgningen ændrer billedet
    imgThressholdedCopy = imgThressholded.copy()

    #Find alle konturer i nummerpladen
    contours, npaHierarchy = cv2.findContours(imgThreshCopy, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    #Loop gennem alle konturerne
    for contour in contours:
        #Opret objekter af klassen classPossibleChar
        possibleChar = classPossibleChar.PossibleChar(contour)
        #Hvis mulig char gem char objektet i listen.
        #Anvender egen funktion til kontrollen.
        if checkIfPossibleChar(possibleChar):
            listOfPossibleChars.append(possibleChar)
    return listOfPossibleChars

#Funktion der undersøger om det mulige bogsatv lever op til krav.
def checkIfPossibleChar(possibleChar):
    if (possibleChar.boundingRectArea > MIN_PIXEL_AREA and
        possibleChar.boundingRectWidth > MIN_PIXEL_WIDTH and possibleChar.boundingRectHeight > MIN_PIXEL_HEIGHT and
        MIN_ASPECT_RATIO < possibleChar.aspectRatio and possibleChar.aspectRatio < MAX_ASPECT_RATIO):
        return True
    else:
        return False

#Funktion der sorterer chars. Fra start af er alle mulige chars blandet sammen i en stor liste.
#Målet med denne funktion er at arrangere listen således, at det bliver en liste over liter med matchende chars.
def findListOfListsOfMatchingChars(listOfPossibleChars):
    listOfListsOfMatchingChars = []
    #loop gennem chars
    for possibleChar in listOfPossibleChars:
        listOfMatchingChars = findListOfListsOfMatchingChars(possibleChar, listOfPossibleChars)
        #Gem i listen
        listOfMatchingChars.append(possibleChar)
        #Hvis længden af listen med matchende bogstaver er over den fastfastte grænse fortsæt,
        #ellers spring videre til den næste liste.
        if len(listOfMatchingChars) < MIN_NUMBER_OF_MATCHING_CHARS:
            continue

        #Gem i liste med liste over matchende chars
        listOfListsOfMatchingChars.append(listOfMatchingChars)

        #Laver en liste til at fjerne de andre chars således at hvert char ikke bliver machet flere gang.
        listOfPossibleCharsWithMatchesRemoved = []
        #Anvender set() funktionen til at fjerne dem fra listen, og dermed den store pulje af chars
        listOfPossibleCharsWithMatchesRemoved = list(set(listOfPossibleChars) - set(listOfMatchingChars))

        #Kalder sig selv igen, for at få de andre lister med matchende chars
        recursiveListOfListsOfMatchingChars = findListOfListsOfMatchingChars(listOfPossibleCharsWithCurrentMatchesRemoved)      # recursive call
        #Looper igennem lister og gemmer i listen med lister.
        for recursiveListOfMatchingChars in recursiveListOfListsOfMatchingChars:        # for each list of matching chars found by recursive call
            listOfListsOfMatchingChars.append(recursiveListOfMatchingChars)
        break
    return listOfListsOfMatchingChars


def findListOfMatchingChars(possibleChar, listOfChars):
    return listOfMatchingChars

#Funktion der anvender pythagoras til at betstemme distancen mellem to chars
def distanceBetweenChars(firstChar, secondChar):
    x = abs(firstChar.intCenterX - secondChar.intCenterX)
    y = abs(firstChar.intCenterY - secondChar.intCenterY)
    return math.sqrt((x ** 2) + (y ** 2))

def angleBetweenChars(firstChar, secondChar):
    return angleInDeg

def removeInnerOverlappingChars(listOfMatchingChars):
    return listOfMatchingCharsWithInnerCharRemoved

def recognizeCharsInPlate(imgThressholded, listOfMatchingChars):
    return charsCombined
