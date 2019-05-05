import os
import cv2
import numpy as np
import math
import random

import numberplateRec
import imageProcess
import classPossibleChar

#Konstanter til at chekke et bogstav eller tal.
#Disse definerer dermed hvordan et char ser ud.
MIN_PIXEL_WIDTH = 2
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
RESIZED_CHAR_IMAGE_WIDTH = 30
RESIZED_CHAR_IMAGE_HEIGHT = 45
MIN_CONTOUR_AREA = 100

#FIndlæs datasæt
try:
    labels = np.loadtxt("labelStor.txt", np.int32)
    flattenedImages = np.loadtxt("flattened_imagesStor.txt", np.float32)

except:
    print("Træningsdataen kunne ikke åbnes. Har du klassificeret chars inden?\n")
    os.system("pause")

#Set modellen op.
kNearest = cv2.ml.KNearest_create()
labels = labels.reshape((labels.size, 1))
kNearest.setDefaultK(3)
kNearest.train(flattenedImages, cv2.ml.ROW_SAMPLE, labels)


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
            listOfListsOfMatchingCharsInPlate[i].sort(key = lambda matchingChar: matchingChar.centerX)
            #Anvender egen funktion til at fjerne overlap mellem bogstaver
            listOfListsOfMatchingCharsInPlate[i] = removeElementOfOverlappingChars(listOfListsOfMatchingCharsInPlate[i])

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
    contours, npaHierarchy = cv2.findContours(imgThressholdedCopy, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

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
#Med matchende chars menes der, at charsene er af cirka samme form og størrelse, samt at de er beliggende tæt på hinanden.
def findListOfListsOfMatchingChars(listOfPossibleChars):
    listOfListsOfMatchingChars = []
    #loop gennem chars
    for possibleChar in listOfPossibleChars:
        listOfMatchingChars = findListOfMatchingChars(possibleChar, listOfPossibleChars)
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
        recursiveListOfListsOfMatchingChars = findListOfListsOfMatchingChars(listOfPossibleCharsWithMatchesRemoved)      # recursive call
        #Looper igennem lister og gemmer i listen med lister.
        for recursiveListOfMatchingChars in recursiveListOfListsOfMatchingChars:        # for each list of matching chars found by recursive call
            listOfListsOfMatchingChars.append(recursiveListOfMatchingChars)
        break
    return listOfListsOfMatchingChars

#Denne funktion anvendes til samme formål som den tidligere. Til at sortere en stor liste af chars.
#Denne funktion modtager den store liste, sorterer dem efter matchene chars, og returnerer de matchende i en ny liste.
def findListOfMatchingChars(possibleChar, listOfChars):
    listOfMatchingChars = []
    #Loop gennem mulige chars
    for possibleMatchingChar in listOfChars:
        #Hvis det er det samme char, som vi prøver at finde matchende chars til,
        #skal loopet springe den over, og dermed ikke inkludere den i listen med matchende chars.
        if possibleMatchingChar == possibleChar:
            continue

        #Beregn data om muligt matchende char. Disse skal senere bruges til at chekke om de to chars er matchende.
        #Afstand mellem chars
        distanceBetweenChars = distanceBetweenCharsFunction(possibleChar, possibleMatchingChar)
        #Vinkel mellem chars
        angleBetweenChars = angleBetweenCharsFunction(possibleChar, possibleMatchingChar)
        #Ændring i størrelsen - er de cirka samme areal?
        changeInArea = float(abs(possibleMatchingChar.boundingRectArea - possibleChar.boundingRectArea)) / float(possibleChar.boundingRectArea)
        #Ændring i højde og bredde
        changeInWidth = float(abs(possibleMatchingChar.boundingRectWidth - possibleChar.boundingRectWidth)) / float(possibleChar.boundingRectWidth)
        changeInHeight = float(abs(possibleMatchingChar.boundingRectHeight - possibleChar.boundingRectHeight)) / float(possibleChar.boundingRectHeight)

        #Hvis disse beregninger er inden for de fastfastte grænser, skal de tilføjes til listen med matchende chars.
        if (distanceBetweenChars < (possibleChar.diagonalSize * MAX_DIAG_SIZE_MULTIPLE_AWAY) and
            angleBetweenChars < MAX_ANGLE_BETWEEN_CHARS and
            changeInArea < MAX_CHANGE_IN_AREA and
            changeInWidth < MAX_CHANGE_IN_WIDTH and
            changeInHeight < MAX_CHANGE_IN_HEIGHT):
            listOfMatchingChars.append(possibleMatchingChar)

    return listOfMatchingChars

#Funktion der anvender pythagoras til at betstemme distancen mellem to chars
def distanceBetweenCharsFunction(firstChar, secondChar):
    x = abs(firstChar.centerX - secondChar.centerX)
    y = abs(firstChar.centerY - secondChar.centerY)
    return math.sqrt((x ** 2) + (y ** 2))

#Funktion til at bestemme vinkelen mellen to chars ud fra deres center possition
def angleBetweenCharsFunction(firstChar, secondChar):
    adjacent = float(abs(firstChar.centerX - secondChar.centerX))
    opposite = float(abs(firstChar.centerY - secondChar.centerY))

    #Hvis ikke den hosliggende katete er 0, anvend trignometri til at bestemme vinklen.
    #Hvis den er 0, sæt vinklen til 90 grader.
    if(adjacent != 0.0):
        angleinRad = math.atan(opposite/adjacent)
    else:
        angleinRad = 1.57

    #Konverter til grader
    angleInDeg = angleinRad * (180/math.pi)
    return angleInDeg

#Funktion til at håndtere overlap mellem chars. Her bliver den inderste char/den mindste char fjernet.
#Dermed undgås forviring ved genkendelse.
def removeElementOfOverlappingChars(listOfMatchingChars):
    listOfMatchingCharsOverlappingResolved = list(listOfMatchingChars)

    #Loop gennem chars
    for currentChar in listOfMatchingChars:
        for otherChar in listOfMatchingChars:
            if (currentChar != otherChar):

                #Hvis afstanden er mindre end dirgonal afstanden ganget en konstant,
                #altså at afstanden er så lille, at de to chars går ind over hinanden.
                if distanceBetweenCharsFunction(currentChar, otherChar) < (currentChar.diagonalSize * MIN_DIAG_SIZE_MULTIPLE_AWAY):
                    #Fjern det mindste af to chars der går ind over hinanden
                    if currentChar.boundingRectArea < otherChar.boundingRectArea:
                        #Checkr om det er blevet fjernet en gang allerede
                        if currentChar in listOfMatchingCharsOverlappingResolved:
                            listOfMatchingCharsOverlappingResolved.remove(currentChar)
                    else:
                        #Checkr om det er blevet fjernet en gang allerede
                        if otherChar in listOfMatchingCharsOverlappingResolved:
                            listOfMatchingCharsOverlappingResolved.remove(otherChar)
    return listOfMatchingCharsOverlappingResolved

#Funktion til at genkende chars i billedet. Hertil anvendes KNN modellen, der defineret tidligere.
def recognizeCharsInPlate(imgThressholded, listOfMatchingChars):
    charsCombined = ""

    #Find størrlese og lav en tom matrix med den korrekte størrelse.
    #Denne skal anvendes til at gemme et farve billede af nummerpladen. Dette skal bruges således, at det er muligt at tegne i farver oven på.
    height, width = imgThressholded.shape
    imgThresholdedColor = np.zeros((height, width, 3), np.uint8)

    #Sorter chars efter x position. Dermed bliver nummerpladen i den korrekte læseretning.
    #Hertil anvendes en lamda funktion, der finder centerX koordinaten.
    listOfMatchingChars.sort(key = lambda matchingChar: matchingChar.centerX)

    #Lav farve version af nummerpladen
    cv2.cvtColor(imgThressholded, cv2.COLOR_GRAY2BGR, imgThresholdedColor)

    for currentChar in listOfMatchingChars:
        #Tegn regtangler rundt om de forskellige chars
        pt1 = (currentChar.boundingRectX, currentChar.boundingRectY)
        pt2 = ((currentChar.boundingRectX + currentChar.boundingRectWidth), (currentChar.boundingRectY + currentChar.boundingRectHeight))
        cv2.rectangle(imgThresholdedColor, pt1, pt2, numberplateRec.COLOR_GREEN, 2)

        #Klip det enkelte char ud til genkendelse
        imgchar = imgThressholded[currentChar.boundingRectY : currentChar.boundingRectY + currentChar.boundingRectHeight,
                           currentChar.boundingRectX : currentChar.boundingRectX + currentChar.boundingRectWidth]
        #Tilpas størrelsen af det udklippede char
        charResized = cv2.resize(imgchar, (RESIZED_CHAR_IMAGE_WIDTH, RESIZED_CHAR_IMAGE_HEIGHT))
        #Gør billedet flat
        charResized = charResized.reshape((1, RESIZED_CHAR_IMAGE_WIDTH * RESIZED_CHAR_IMAGE_HEIGHT))
        #Konverter til float
        charResized = np.float32(charResized)

        #Lav KNN forudsigelse
        retval, results, neigh_resp, dists = kNearest.findNearest(charResized, k = 3)
        result = str(chr(int(results[0][0])))
        charsCombined = charsCombined + result

    return charsCombined
