import sqlite3

class DBSettings:

    path = None
    login = None
    password = None


class DataBase:

    global_database_path = None
    global_database_connector = None
    global_database_cursor = None
    global_database_tables_list = []
    
    def __init__(self):

        if DBSettings.path == None:
            raise RuntimeError('DBSettings must be configurated at first')

        if self.global_database_path == None:
            self.global_database_path = DBSettings.path
            self.global_database_connector = sqlite3.connect(self.global_database_path)
            self.global_database_cursor = self.global_database_connector.cursor()
            self.cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\';')
            self.global_database_tables_list = list(map(lambda t: t[0], self.cursor.fetchall()))

    @property
    def connector(self):
        return self.global_database_connector

    @property
    def cursor(self):
        return self.global_database_cursor

    def createTable(self, table_name, **columns_types):
        if table_name not in self.global_database_tables_list:

            columns_description = ',\n    '.join(map(lambda pair: f'{pair[0]} {pair[1].upper()}', columns_types.items()))

            self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}_table (
                {columns_description}
            );''')

    
