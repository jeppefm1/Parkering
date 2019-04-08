import numberplateRec
import numpy as np
import datetime
import mysql.connector

IMAGE =  "Billeder/5.png"
ENTID = 1
MODE = "EXIT"

db = mysql.connector.connect(
  host="35.228.118.25",
  user="Python",
  passwd="84n$RmH8kQ*g",
  database="Data")

def main():
    numberplate = numberplateRec.main(IMAGE)
    print("Nummerplade fundet: ", numberplate)

    if(MODE == "ENTER"):
        addToEnteredLog(numberplate)
    elif (MODE == "EXIT"):
        addToExitLog(numberplate)


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
