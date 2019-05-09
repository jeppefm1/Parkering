import numpy as np
import sys
import cv2
import os

#Constanter der definerer bogstaver
CONTOUR_AREA_MINIMUM = 70
RESIZED_IMAGE_WIDTH = 30
RESIZED_IMAGE_HEIGHT = 45
IMAGE_PATH = 'DanskTraining.png'

#Henter billede med træningsdata
imgTrainingData = cv2.imread(IMAGE_PATH)

#Check for failure
if (imgTrainingData is None):
    print("Failure in opening image - Check image path")
else:
    #Gråskaller billede
    imgGrayscale = cv2.cvtColor(imgTrainingData, cv2.COLOR_BGR2GRAY)
    #Gør billedet sløret
    imgBlur = cv2.GaussianBlur(imgGrayscale, (5,5), 0)
    #Thresshold billedet - dermed bliver grå lavet om til sort og hvidt. Skaber dermed konstraster
    #adaptiveThreshold(src, maxValue, adaptiveMethod, thresholdType, blockSize, C[, dst])
    imgThressholded = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    #Vis behandlet billede
    cv2.imshow("Behandlet billede", imgThressholded)

    #Lvaer copi af billede, da findContours laver om på billedet
    imgThressholdedCopy = imgThressholded.copy()

    #Finder de yderste konturer, ved at forbinde punkter
    imgContours, imgHierarchy = cv2.findContours(imgThressholdedCopy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #Laver et tomt 1D array, hvor alt billededataen kan gemmes
    imagesFlattend = np.empty((0, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT),dtype=np.float32)

    #Array til at gemme labels
    imgClassifications = []

    validChars = [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9'),
                     ord('A'), ord('B'), ord('C'), ord('D'), ord('E'), ord('F'), ord('G'), ord('H'), ord('I'), ord('J'),
                     ord('K'), ord('L'), ord('M'), ord('N'), ord('O'), ord('P'), ord('Q'), ord('R'), ord('S'), ord('T'),
                     ord('U'), ord('V'), ord('W'), ord('X'), ord('Y'), ord('Z')]
    #Loop gennem konturer. Undersøger om konturer ligner bogstaver
    for imgContour in imgContours:
        #Er konturens areal større end minimums bogstavet?
        if (cv2.contourArea(imgContour) > CONTOUR_AREA_MINIMUM):
            #Gem koordinater og størrelse
            [x, y, w, h] = cv2.boundingRect(imgContour)
            #Tegn en rød regtangel omkring konturer
            cv2.rectangle(imgTrainingData, (x,y), (x+w, y+h), (0,0,255), 2)
            #Find konturen i det behandlede billede, og beskær billedet
            contourProcessed = imgThressholded[y:y+h, x:x+w]
            contourProcessedResized = cv2.resize(contourProcessed, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))
            #Vis billeder
            cv2.imshow("Behandlet kontour", contourProcessedResized)
            cv2.imshow("Dataopsamling", imgTrainingData)
            #Venter på bruger, der klassificerer kontour
            char = cv2.waitKey(0)
            #Chekker om keyboard input er et muligt input i listen med gyldige tegn.
            if(char in validChars):
                print("Valid char found")
                #Gemmer label i listen med labels
                imgClassifications.append(char)
                #Gør billedet flat
                flattendImg = contourProcessedResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
                #Gemmer det flade billede i listen med flade billeder
                imagesFlattend = np.append(imagesFlattend, flattendImg, 0)
            else:
                #Prøv at intaste char igen
                print("FEJL - Ikke gyldigt bogstav - STORE BOGSTAVER PÅKRÆVET! - Aktiver Caps Lock og prøv igen")
                intChar = cv2.waitKey(0)
                #print("IntChar", intChar)
                #Chekker om keyboard input er et muligt input i listen med gyldige tegn.
                if(intChar in validChars):
                    print("Valid char found")
                    #Gemmer label i listen med labels
                    imgClassifications.append(intChar)
                    #Gør billedet flat
                    flattendImg = contourProcessedResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
                    #Gemmer det flade billede i listen med flade billeder
                    imagesFlattend = np.append(imagesFlattend, flattendImg, 0)

                else:
                    cv2.waitKey(0)
                    sys.exit()

    #Laver labels om til et 1D array af floats.
    labelsArray = np.array(imgClassifications, dtype=np.int32)
    labelsArrayReshaped = np.reshape(labelsArray,(labelsArray.size, 1))

    #Lukker vinduer
    cv2.destroyAllWindows()
    print("Data indsamlet - Gemmer data")

    #Gemmer datasæt
    np.savetxt("labelStor.txt", labelsArrayReshaped)
    np.savetxt("flattened_imagesStor.txt", imagesFlattend)

    print("Model saved to file.")
