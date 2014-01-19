#!/usr/bin/python
# Logger.py
# non-gui portions of the time logger
# Uses sqlite3 as the database

import sqlite3
import re
import os
import time

names = []  # first, last
cursor = None
CT = "CREATE TABLE IF NOT EXISTS members(first TEXT, last TEXT, logtime INTEGER, action TEXT)"

class Logger:

    def __init__(self):
        self.names = []
        self.conn = None
        self.c = None # db cursor

        self.initNames()
        self.connectToDB()

    def initNames(self):
        tempfname = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "people.csv")
        namesfile = open(tempfname, "r")

        for line in namesfile.readlines():
            temp = re.split(",", line)
            # strip the newline
            temp[1] = temp[1].rstrip()
            self.names.append(tuple(temp))

        self.names = sorted(self.names, key=lambda x: x[1])

        namesfile.close()

    def connectToDB(self):
        self.conn = sqlite3.connect("people.db")
        self.c = self.conn.cursor()
        self.c.execute(CT)
        self.conn.commit()

    def getInfo(self, first=None, last=None):
        if first or last:
            for name in self.names:
                if name[0] == first or name[1] == last:
                    return name
        else:
            return (None, None)
    
    def getLastAction (self, first, last):
        self.c.execute("SELECT * FROM members WHERE " + \

                       "first=(?) AND last=(?)", [first, last])
        self.conn.commit()

        results = sorted(self.c.fetchall(), key=lambda x: x[2])
        if not results == []:
            return results[-1][-1]
        else:
            return None

    def log(self, first, last, action):
        
        t = int(time.time())

        person = self.getInfo(first, last)
        self.c.execute("INSERT into members VALUES(?,?,?,?)",
                       [first, last, t, action])
        self.conn.commit()
    
    def logOutAll(self):
        for name in self.names:
            if self.getLastAction(name[0], name[1]) == "in":
                self.log(name[0], name[1], "out")

    def addNewMember(self, first, last):
        fh = open(os.path.join(os.path.dirname(__file__),
                  "people.csv"), "a")
        fh.write(first + "," + last + "\n")
        fh.close()

if __name__ == "__main__":
    logger = Logger()
    logger.addNewUser("NEW", "NAME")

