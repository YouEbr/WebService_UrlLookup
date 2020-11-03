import json


# reads db_config.json and returns the configuration to the caller.
def read_conf(config_file):
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

    return DatabaseName, TableName, ColumnName, ConnectionInfo
