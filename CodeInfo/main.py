# set up connection
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DBInfo.db_connection import connection, cursor

#function

def main():
    # get the path of this file (optional, kept for later use)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sqlfile_path = os.path.abspath(os.path.join(dir_path, "..", "DBInfo", "football.sql")) #avoids fixing the code because other users will have their path

    #access the SQL file
    with open(sqlfile_path, "r", encoding="utf-8") as f:
        sql_code = f.read()
    
    #cursor.execute(sql_code)
    #connection.commit() #if needed for later

    print("Connection works; SQL not yet executed.")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()
