from typing import Sequence
import mariadb
import sys
from .config import basedata

class mysql():
    def __init__(self):
        self.data = []
        pass

    def connect(self):
        #print('connecting to db')
        try:
            self.conn = mariadb.connect(
                user=basedata.user,
                password=basedata.password,
                host=basedata.host,
                port=basedata.port,
                database=basedata.database
            )
            return self.conn.cursor(buffered=True)

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return False

    def disconnect(self):
        try: self.conn.close()
        except: return False

    def select(self, select: str='', fromtable: str="", where: tuple=()):
        # Get Cursor
        curr = self.connect()
        if curr is False:
            return False

        cmd = f"SELECT {select} FROM {fromtable}"
        arg = None
        if where:
            cmd += f" WHERE {where[0]}=?"
            arg = where[1]
            curr.execute(cmd, (arg,))
        else:
            curr.execute(cmd)

        self.conn.commit()
        self.data = [data for data in curr]
        self.disconnect()
        return self.data
        
    def insert(self, select:str = "", fromtable:str = "", values: tuple=()):
        curr = self.connect()
        if curr is False:
            return False

        cmd = f"INSERT INTO {fromtable} ({select}) VALUES {values};"
        curr.execute(cmd)
        self.conn.commit()
        self.disconnect()
        return True
    
    def update(self, values: str="", table: str="", filter: tuple=()):
        curr = self.connect()
        if curr is False:
            return False
        
        cmd = f"UPDATE {table} SET {values}"
        arg = None
        if filter:
            cmd += f" WHERE {filter[0]}=?"
            arg = filter[1]
            cmd += ';'
            curr.execute(cmd, (arg,))
        else:
            cmd += ';'
            curr.execute(cmd)

        self.conn.commit()
        self.disconnect()
        return True

    def tables(self):
        curr = self.connect()
        if curr is False:
            return False

        curr.execute("show tables;")
        self.conn.commit()
        self.data = [data[0] for data in curr]
        self.disconnect()
        return self.data

    def run(self, cmd):
        curr = self.connect()
        if curr is False:
            return False
        
        curr.execute(cmd)
        self.conn.commit()
        #self.data = [data for data in curr]
        self.disconnect()
        return self.data

    def create_matchTable(self, title: str=""):
        curr = self.connect()
        if curr is False:
            return False

        cmd = f"CREATE TABLE {title}" + basedata.match_create
        curr.execute(cmd)
        self.conn.commit()
        self.disconnect()
        return True