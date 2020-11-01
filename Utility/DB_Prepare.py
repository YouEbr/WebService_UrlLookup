#####################################################################
# The utility that creates and populates a DB/table with malware urls.
# Load the DB info out of ../Config/db_config.json
#####################################################################

import mariadb
import json

config_file = "../Config/db_config.json"


# reads db_config.json and returns the configuration to the caller.
def read_conf():
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except (IOError, PermissionError):
        print(f'ERROR: Unable to read {config_file}')
        exit(-1)
    except json.decoder.JSONDecodeError:
        print(f'ERROR: Malformed {config_file}')
        exit(-1)

    DatabaseName = config['DatabaseName']
    TableName = config['TableName']
    ColumnName = config['ColumnName']
    ConnectionInfo = config['ConnectionInfo']

    return DatabaseName, TableName, ColumnName, ConnectionInfo


def create_db(cursor, db_name):
    try:
        cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(db_name))
    except mariadb.Error as err:
        print("Failed to create database {} with error {}".format(db_name, err))
        exit(1)


def main():
    DatabaseName, TableName, ColumnName, ConnectionInfo = read_conf()
    with mariadb.connect(**ConnectionInfo) as conn:
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

        with open("SampleMalwareList.txt") as file:
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


if __name__ == '__main__':
    main()
