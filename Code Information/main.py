#set up connection
import os
from DBInfo.db_connection import get_connection

#get path of file if needed later
dir_path = os.path.dirname(os.path.realpath(__file__))

def main():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('''SELECT NOW();''')
    print("Connection successfully made.")

    connection.commit()

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()