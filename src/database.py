"""
Database.py

Deals with all the database connections.
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
            `flags` TEXT NOT NULL,
            `deadline` TEXT NOT NULL
        )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS `questions` (
            `function` TEXT NOT NULL UNIQUE,
            `points` INT NOT NULL,
            `type` TEXT NOT NULL,
            `criteria` TEXT NOT NULL,
            `flags` TEXT NOT NULL
        )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS `users` (
            `key` TEXT NOT NULL UNIQUE,
            `name` TEXT NOT NULL,
            `role` TEXT DEFAULT 'user',
            `submissions` TEXT DEFAULT '{}'
        )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS `submissions` (
            `id` TEXT NOT NULL UNIQUE,
            `results` TEXT NOT NULL,
            `score` INT NOT NULL
        )''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS `competitions` (
            `name` TEXT NOT NULL UNIQUE,
            `assignment` TEXT NOT NULL,
            `deadline` TEXT NOT NULL,
            `status` TEXT DEFAULT 'inactive',
            `startedAt` TEXT,
            `submissions` TEXT DEFAULT '{}'
        )''')

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

    ### Deal with user data. ###
    def getUsers(self):
        rows = self.cur.execute('SELECT * FROM `users` WHERE role="user"')
        return rows.fetchall()

    def getUser(self, id):
        rows = self.cur.execute('SELECT * FROM `users` WHERE key = ?', (id, ))
        return rows.fetchone()

    def createSubmission(self, id: str, results, score):
        self.cur.execute('INSERT INTO `submissions` (id, results, score) VALUES (?, ?, ?)', (id, results, score))
        self.saveChanges()

    def getSubmission(self, id: str):
        rows = self.cur.execute('SELECT * FROM `submissions` WHERE id = ?', (id, ))
        return rows.fetchone()

    def newUser(self, id: str, name, role='user'):
        self.cur.execute('INSERT INTO `users` (key, name, role) VALUES (?, ?, ?)', (id, name, role))
        self.saveChanges()

    def newUserSubmission(self, id: str, submission):
        self.cur.execute('UPDATE `users` SET submissions = ? WHERE key = ?', (submission, id))
        self.saveChanges()

    def getUserSubmissions(self, id: str, name):
        rows = self.cur.execute('SELECT * FROM `users` WHERE key = ?', (id, ))
        user = rows.fetchone()

        if user == None:
            self.newUser(id, name)
            return self.getUserSubmissions(id, name)
        else:
            return user

    ### Deal with assignments ###

    def getAssignments(self):
        rows = self.cur.execute(f'SELECT * FROM assignments')
        return rows.fetchall()

    def getAssignment(self, name):
        rows = self.cur.execute(f'SELECT * FROM `assignments` WHERE `name` = ?', (name, ))
        return rows.fetchone()
    
    def deleteAssignment(self, name):
        x = self.cur.execute(f'DELETE FROM `assignments` WHERE name = ?', (name, ))

        if x.rowcount == 0:
            raise Exception('No such assignment exists')
        else:
            self.saveChanges()
            return True

    def deleteQuestion(self, name):
        x = self.cur.execute(f'DELETE FROM `questions` WHERE function = ?', (name, ))

        if x.rowcount == 0:
            raise Exception('No such question exists')
        else:
            self.saveChanges()
            return True

    def getTests(self, function):
        rows = self.cur.execute('SELECT * FROM `questions` WHERE function = ?', (function, ))
        return rows.fetchone()


    ### Deal with competitions ###
    def getCompetition(self, name):
        rows = self.cur.execute('SELECT * FROM `competitions` WHERE name = ?', (name, ))
        return rows.fetchone()

    def getCompetitions(self):
        rows = self.cur.execute('SELECT * FROM `competitions` WHERE status="active"')
        return rows.fetchall()

    def setCompetitionStatus(self, name, status, time):
        self.cur.execute('UPDATE `competitions` SET status = ?, startedAt = ? WHERE name = ?', (status, time, name))
        self.saveChanges()
    
    def getCompetitionSubmissions(self, name):
        rows = self.cur.execute('SELECT submissions FROM `competitions` WHERE name = ?', (name, ))
        return rows.fetchone()

    def updateCompetitionSubmissions(self, name, new):
        self.cur.execute('UPDATE `competitions` SET submissions = ? WHERE name = ?', (new, name))
        self.saveChanges()

    def deleteCompetition(self, name):
        self.cur.execute(f'DELETE FROM `competitions` WHERE name = ?', (name, ))
        self.saveChanges()

    # Commits the changes.
    def saveChanges(self):
        self.con.commit()

    
if __name__ == "__main__":
    myDb = db()
    # myDb.create('assignments',  name='hello', questions='{1, 2, 3}', flags='{}')
    # print(myDb.getAssignments())
    print(myDb.getUserSubmissions(472521286807977994))
    # print(myDb.getAssignment('hello1'))