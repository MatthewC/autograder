"""
Database.py
"""
import sqlite3 as sl
import os

class db(object):
    def __init__(self):
        if not os.path.exists('./config'):
            os.mkdir('./config')
        
        self.con = sl.connect(f'./config/data.db')
        self.cur = sl.Cursor(self.con, )
        self.cur.row_factory = sl.Row

        self.initilizeTables()

    def initilizeTables(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS `assignments` (
            `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `name` TEXT NOT NULL UNIQUE,
            `questions` TEXT NOT NULL,
            `flags` TEXT NOT NULL
        )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS `users` (
            `key` TEXT NOT NULL UNIQUE,
            `role` TEXT DEFAULT 'user'
        )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS `questions` (
            `function` TEXT NOT NULL UNIQUE,
            `points` INT NOT NULL,
            `type` TEXT NOT NULL,
            `criteria` TEXT NOT NULL,
            `flags` TEXT NOT NULL
        )''') #should default to {}

    def create(self, table, **kwargs):
        columns = ""
        values = ""
        for arg in kwargs:
            columns += f'{arg}, '
            values += '?, '
        columns = columns[:-2]
        values = values[:-2]
        self.cur.execute(f'''INSERT INTO `{table}` ({columns}) VALUES ({values})''', tuple(kwargs.values()))
        self.saveChanges()
        return


    def update(self, reference, new):
        pass

    def getAssignments(self):
        rows = self.cur.execute(f'''SELECT * FROM assignments''')
        return rows.fetchall()

    def getAssignment(self, name):
        rows = self.cur.execute(f'SELECT * FROM `assignments` WHERE `name` = ?', (name,))
        print(rows.fetchall())
        return rows.fetchone()
    
    def deleteAssignment(self, name):
        x = self.cur.execute(f'DELETE FROM `assignments` WHERE name = ?', (name,))

        if x.rowcount() == 0:
            raise Exception('No such assignment exists')
        else:
            self.saveChanges()
            return True

    # Commits the changes.
    def saveChanges(self):
        self.con.commit()

    
if __name__ == "__main__":
    myDb = db()
    myDb.create('assignments',  name='hello', questions='{1, 2, 3}', flags='{}')
    print(myDb.getAssignments())
    # print(myDb.getAssignment('hello1'))