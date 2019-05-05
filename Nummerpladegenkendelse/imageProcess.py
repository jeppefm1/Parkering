import cv2
import numpy as np
import math

#Konstanter til billedebehandlingen
FILTER_SIZE_GAUSSIAN = (5,5)
#Thresshold konstanter - skal være ullige
#Bestemmer den måde billedet bliver binært simplificeret
THRESSHOLD_BLOCKSIZE = 21
THESSHOLD_WEIGHT = 11

def preprocessImg(imgUnprocessed):
    #Anvend egen funktion til at Grayscale billedet, anvender HSV metoden - nærmere beskrevet i funktionen.
    imgGrayscaled = HSVGrayscale(imgUnprocessed)
    #Anvender egen funktion til at fjerne støj fra subjekt og baggrund. Metode nærmere beskrevet i funktionen.
    imgDenoised = removeNoise(imgGrayscaled)
    #Finder billedets dimmensioner
    height, width = imgGrayscaled.shape
    #Slører billedet, hertil laves først et tomt array.
    imgBlurred = np.zeros((height, width, 1), np.uint8)
    #Anvender en gaussisk funktion til sløringen.
    imgBlurred = cv2.GaussianBlur(imgDenoised, FILTER_SIZE_GAUSSIAN, 0)
    #Thressholder billedet - hvilket betyder at billedet bliver binært simplificeret.
    #Prøver dermed at lave billedet sort hvidt.
    #Anvender en adaptiv funktion i cv2, der kigger billedet og tilpasser metoden til sort hvid konverteringen.
    imgThressholded = cv2.adaptiveThreshold(imgBlurred, 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, THRESSHOLD_BLOCKSIZE, THESSHOLD_WEIGHT)
    return imgGrayscaled, imgThressholded


def HSVGrayscale(imgUnprocessed):
    #Et billede kan også beskrive som  HSV (hue, saturation, value), der er et alternativ til RGB.
    #Den ene værdi beskriver billedet som gråskaleret, og denne kan derfor udtrækkes ved transformationen.

    #Henter dimmensionerne fra billedet
    height, width, numChannels = imgUnprocessed.shape
    #Laver tomt array til transformeret billede
    imgHSV = np.zeros((height, width, 3), np.uint8)
    #Transformer billede til HSV
    imgHSV = cv2.cvtColor(imgUnprocessed, cv2.COLOR_BGR2HSV)
    #Gemmer værdier i tre variabler
    imgHue, imgSaturation, imgValue = cv2.split(imgHSV)
    #Skal kun bruge value, der svarer til Grayscale
    return imgValue

def removeNoise(imgGrayscaled):
    #Funktionen laver flere Morphological Transformations, der har til hensigt at fjerne støj.
    #https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
    #https://www.youtube.com/watch?v=YA5u2PI3hF0
    #Der findes foskellige typer:
        #Opening fjerner false positive i baggrunden
        #Closeing fjerner false negative i subjektet
        #Tophat - forskel mellem input og opening af input billedet
        #Blackhat - forskel mellem input og closing af input billedet

    height, width = imgGrayscaled.shape
    #Tomme numpy arrays til Tophat og Blackhat
    imgTopHat = np.zeros((height, width, 1), np.uint8)
    imgBlackHat = np.zeros((height, width, 1), np.uint8)
    #Form der anvendes til tranformationerne. Her anvendes en regtangel.
    structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    #Laver tophat og blackhat transformationer - se foklaring over.
    imgTopHat = cv2.morphologyEx(imgGrayscaled, cv2.MORPH_TOPHAT, structuringElement)
    imgBlackHat = cv2.morphologyEx(imgGrayscaled, cv2.MORPH_BLACKHAT, structuringElement)
    #Lægger billederne sammen - Grayscale + tophat - blackhat
    imgGrayscalePlusTopHat = cv2.add(imgGrayscaled, imgTopHat)
    imgGrayscalePlusTopHatMinusBlackHat = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)
    return imgGrayscalePlusTopHatMinusBlackHat
