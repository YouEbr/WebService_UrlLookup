#####################################################################
# The utility that creates and populates a DB/table with malware urls.
# Load the DB info out of ../Config/db_config.json
#####################################################################
import os
import mariadb
from Utility.DB_Config_Loader import read_conf
from time import sleep

sampleList = "SampleMalwareList.txt"
MAX_RETRIES_NUM = 15


def create_db(cursor, db_name):
    try:
        cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(db_name))
    except mariadb.Error as err:
        print("Failed to create database {} with error {}".format(db_name, err))
        exit(1)


def main():
    DatabaseName, TableName, ColumnName, ConnectionInfo = read_conf()
    successful_connection = False
    retry_num = 1
    while (not successful_connection) and (retry_num < MAX_RETRIES_NUM):
        try:
            with mariadb.connect(**ConnectionInfo) as conn:
                successful_connection = True
                cursor = conn.cursor()
                try:
                    cursor.execute("USE {}".format(DatabaseName))
                except mariadb.Error:
                    print("Database \"{}\" does not exist, Creating it.".format(DatabaseName))
                    create_db(cursor, DatabaseName)
                    cursor.execute("USE {}".format(DatabaseName))

                try:
                    cursor.execute("DROP TABLE IF EXISTS {}".format(TableName))
                except mariadb.Error as err:
                    print("Error while dropping {} ".format(TableName))
                    print(err)

                try:
                    cursor.execute("CREATE TABLE {} (url TEXT)".format(TableName))
                except mariadb.Error as err:
                    print("Error while creating {} ".format(TableName))
                    print(err)

                file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sampleList)
                print(file_path)
                with open(file_path) as file:
                    for url in file:
                        try:
                            cursor.execute(
                                '''INSERT INTO {} ({}) VALUES ("{}")'''.format(TableName, ColumnName, url.strip('\n')))
                        except mariadb.Error as err:
                            print("Error while data insertion into {} ".format(TableName))
                            print(err)

                conn.commit()
                cursor.execute("""SELECT COUNT(*) FROM {}""".format(TableName))
                print("{} urls have been added to {} table of {} database".format(cursor.fetchall()[0][0], TableName,
                                                                                  DatabaseName))
        except mariadb.Error as err:
            if "Can't connect to" in str(err):
                print(err)
                print("Sleeping for 1 seconds before retrying...")
                sleep(1)
                retry_num += 1
            elif "Unknown MySQL server host" in str(err):
                print("Unknown MariaDB server host \'{}\'.\n Check DB's hostname and try again. Exiting")
                exit(-1)
            elif "Access denied for user" in str(err):
                print("Access to MariaDB server denied.\nCheck the credentials for the MariaDB and try again. Exiting")
                exit(-1)

    if retry_num == MAX_RETRIES_NUM:
        print("Could not connect to database server. Exiting...")
        exit(-1)


if __name__ == '__main__':
    main()
