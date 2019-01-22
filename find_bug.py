#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @package    
# @brief      
#
# @version 
# @author     Sergey Green
# @note       
#

import sys
import os
import re
import sqlite3 as lite
from optparse import OptionParser

class NoneValue(Exception):
    """None value..."""
    pass

class NotFound(Exception):
    """Not found..."""
    pass

class FindBug:
    def __init__(self):
        """FindBug main class"""
        
        self.legs = '\|\ \|'
        self.body = '###O'
        self.db = sys.argv[0].replace(".py", ".db")
        
    def collectArgs(self):
        parser = OptionParser(usage="""usage: %prog [Options] ..""")
        parser.add_option("-l", "--landscape",
            dest="landscape",
            default=None,
            help="Landscape file, default=None",)
        (self.opts, args) = parser.parse_args() 
            
    def verifyArgs(self):          
        for opt, value in self.opts.__dict__.items():  
            try:
                if value:
                    setattr(self, opt, value)
                else:
                    raise NoneValue
                if not os.path.isfile(value):
                    raise NotFound
                        
            except NoneValue:
                print "%s parameter has no value .." % opt
                exit(1)
            except NotFound:
                print "%s was not found .." % value
                exit(1)
                    
    def createDb(self):
        if not os.path.exists(self.db):
            try:
                conn = lite.connect(self.db)
            except lite.Error, e:
                print "Error %s:" % e.args[0]
                sys.exit(1)
            finally:
                if conn: conn.close()
        else: pass
            
    def createTable(self):    
        try:
            conn = lite.connect(self.db)
            cur = conn.cursor()  
            cur.executescript("""
                DROP TABLE IF EXISTS PARTS;
                CREATE TABLE IF NOT EXISTS PARTS
                (
                    lnumber INTEGER,
                    Part    VARCHAR(5),
                    Start   INTEGER
                )
                """)
            conn.commit()
        except lite.Error, e:
            if conn: conn.rollback()
            print "Error %s:" % e.args[0]
            sys.exit(1)
        finally:
            if conn: conn.close()
                
    def insertRow(self, lnumber, part, start):
        conn = lite.connect(self.db)
        cur = conn.cursor()
        cur.execute('''INSERT INTO PARTS VALUES (?,?,?);''', (lnumber, part, start))
        conn.commit()
        conn.close()
            
    def selectRow(self, lnumber, part, start):
        conn = lite.connect(self.db)
        with conn:
            cur = conn.cursor()
            sql = """
                SELECT * FROM PARTS WHERE
                Lnumber = '%s' AND
                Part = '%s' AND
                Start = '%s'
            """ % (lnumber, part, start)
            cur.execute(sql)
            return cur.fetchone()
                
    def readLandscape(self):
        with open(self.landscape, 'r') as landscape:
            lnumber = 0
                
            for l in landscape.readlines():
                line = l.replace("\n", "")
                
                for match_legs in re.finditer(self.legs, line):
                    if match_legs:
                        legs = match_legs.start()
                        self.insertRow(lnumber, "legs", legs)
                            
                match_body = re.search(self.body, line)
                    
                if match_body:
                    body = match_body.start()
                    self.insertRow(lnumber, "body", body)  
                lnumber += 1
                    
    def findBug(self):
        found_count = 0
        conn = lite.connect(self.db)
        with conn:
            cur = conn.cursor()    
            cur.execute("SELECT Lnumber, Part, Start FROM PARTS where Part = 'body'")
            while True:
                row = cur.fetchone()
                if row == None:
                    break
                        
                if (row[0] and self.selectRow(int(row[0]) -1, "legs", row[2]) and self.selectRow(int(row[0]) -1, "legs", row[2])):
                    found_count += 1
                        
        self.printFound(found_count)
            
    def printFound(self, found_count):
        print "Found %d bugs .." % found_count
        
    def removeDb(self):
        if os.path.isfile(self.db):
            os.remove(self.db)
            
def main():
    fb = FindBug()
    fb.collectArgs()
    fb.verifyArgs()
    fb.createDb()
    fb.createTable()
    fb.readLandscape()
    fb.findBug()
    fb.removeDb() 
    
if __name__ == '__main__':
    main()

