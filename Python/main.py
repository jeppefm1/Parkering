import numberplateRec
import numpy as np
import datetime
import mysql.connector
import msvcrt as m

IMAGE =  "Billeder/"
ENTID = 1
MODE = "EXIT"
PI = False

if (PI == True):
    import LCD
    #Klargør display
    lcd.lcd_init()

db = mysql.connector.connect(
  host="35.228.118.25",
  user="Python",
  passwd="84n$RmH8kQ*g",
  database="Data")

def main():
    print("Tryk på mellemrum for at lede efter nummerplade")
    while True:
        char = input("Hvilket billede ønsker du at genkede? \n Billede: ")
        try:
            numberplate = numberplateRec.main(IMAGE + char + ".png")
            print("Nummerplade fundet: ", numberplate)

            if(MODE == "ENTER"):
                addToEnteredLog(numberplate)
                print("Nummerplade tilføjet til indkørsel log \n \n")
                if (PI == True and numberplate == ""):
                    lcd_string("Velkommen til",LCD_LINE_1)
                    lcd_string("Parkering.tk",LCD_LINE_2)
                elif (PI == True):
                     lcd_string("Nummerplade",LCD_LINE_1)
                     lcd_string("fundet: " + numberplate,LCD_LINE_2)
                     time.sleep(5)
                     numberplate=""

            elif (MODE == "EXIT"):
                addToExitLog(numberplate)
                print("Nummerplade tilføjet til udkørsel log \n \n")
                if (PI == True and numberplate == ""):
                    lcd_string("Vi ses igen :D",LCD_LINE_1)
                    lcd_string("Parkering.tk",LCD_LINE_2)
                elif (PI == True):
                     lcd_string("Nummerplade",LCD_LINE_1)
                     lcd_string("fundet: " + numberplate,LCD_LINE_2)
                     time.sleep(5)
                     numberplate=""

        except Exception as e:
            pass


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
