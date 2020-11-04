import json
import os

config_file = "../Config/db_config.json"


# reads db_config.json and returns the configuration to the caller.
def read_conf():
    cw = os.getcwd()  # save current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # change to current files location

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except (IOError, PermissionError):
        print(f'ERROR: Unable to read {config_file}')
        exit(-1)
    except json.decoder.JSONDecodeError:
        print(f'ERROR: Malformed {config_file}')
        exit(-1)

    DatabaseName = config['Database']
    TableName = config['Table']
    ColumnName = config['Column']
    ConnectionInfo = config['ConnectionInfo']

    os.chdir(cw)  # change to what was the current directory before this method was called.

    return DatabaseName, TableName, ColumnName, ConnectionInfo
