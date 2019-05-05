import numberplateRec
import numpy as np
import datetime
from serial import Serial
import mysql.connector
import cv2
import time

ENTID = 1
MODE = "ENTER"

#Åbner serial port
serial = Serial('COM7', 9600, timeout=1)
time.sleep(2)

db = mysql.connector.connect(
  host="35.228.118.25",
  user="Python",
  passwd="84n$RmH8kQ*g",
  database="Data")

def main():
    #Tænder webcam
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Leder efter nummerplade")

    while True:
        try:
            #Hvis der trykkes på mellemrum skal det nuværende frame gemmes.
            read, frame = cam.read()
            cv2.imshow("Leder efter nummerplade", frame)
            if not read:
                break
            k = cv2.waitKey(1)

            if k%256 == 27:
                # ESC pressed
                print("Escape hit, closing...")
                break
            elif k%256 == 32:
                # SPACE pressed
                img_name = "opencv_frame.png"
                cv2.imwrite(img_name, frame)
                print("{} written!".format(img_name))
                cam.release()
                cv2.destroyAllWindows()

                #Undersøg det gemte frame for nummerplader
                numberplate = numberplateRec.main("opencv_frame.png")
                if (numberplate != None):
                    print("Nummerplade fundet: ", numberplate)

                #Hvis nummerplade fundet og mode er ENTER gem i indkørsel log
                if(MODE == "ENTER"):
                    if (numberplate != None):
                        addToEnteredLog(numberplate)
                        print("Nummerplade tilføjet til indkørsel log \n \n")
                        #Sender nummerplade til arduino
                        arduino(numberplate)

                #Hvis nummerplade fundet og mode er EXIT gem i udkørsel log
                if(MODE == "EXIT"):
                    if (numberplate != None):
                        addToExitLog(numberplate)
                        print("Nummerplade tilføjet til udkørsel log \n \n")
                        #Sender nummerplade til arduino
                        arduino(numberplate)

                cam = cv2.VideoCapture(0)
                cv2.namedWindow("Leder efter nummerplade")

        except AssertionError as e:
            print(e)

def arduino(numberplate):
    encode = str('{}\n'.format(numberplate)).encode('UTF-8')
    serial.write(encode)
    print("Har sendt følgende til arduino: ", encode)

def addToEnteredLog(numberplate):
    #Tilføj nummerplade til indkørsel log
    sql_insert_query = "INSERT INTO main_log (numberplate, entered, entid) VALUES ('{}', CURRENT_TIME(), {});".format(numberplate, ENTID)
    cursor = db.cursor()
    result  = cursor.execute(sql_insert_query)
    db.commit()
    return

def addToExitLog(numberplate):
    #Find det nyeste ID i loggen for bilens indkørsel
    cursor = db.cursor()
    sql_select_query = "SELECT `id` FROM main_log WHERE numberplate = '{}' ORDER BY `id` DESC LIMIT 1; ".format(numberplate)
    cursor.execute(sql_select_query)
    result = cursor.fetchone()

    #TIlføj udkørsel til række i loggen, anvender id fra tidligere forespøgsel
    sql_update_query = "UPDATE main_log set exited = CURRENT_TIME() where id ='{}'".format(result[0])
    result  = cursor.execute(sql_update_query)
    db.commit()

    #Verificer nummerpladen på hjemmesiden
    sql_update_query = "UPDATE main_plates set state = 0 where plateNumber ='{}'".format(numberplate)
    result  = cursor.execute(sql_update_query)
    db.commit()
    return

if __name__ == '__main__':
    main()
    serial.close()
