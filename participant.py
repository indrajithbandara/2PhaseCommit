from SimpleXMLRPCServer import SimpleXMLRPCServer
import sqlite3 as lite
import sys

class Participant:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.log = file(self.name + '.log', 'a+')

        try:
            self.conn = lite.connect(self.name+ '.db')
            self.cur = self.conn.cursor()
            self.cur.execute('CREATE TABLE IF NOT EXISTS Info(key INT PRIMARY KEY, value TEXT)')
            self.conn.commit()
        except lite.Error, e:
            print "Error %s"%e.args[0]
            sys.exit()

    def par_recover(self):
        last_line = ""
        self.file = open(self.name + ".log", "r+")
        for line in self.file:
            last_line= line
        param = last_line.split(" ")
        if(str(param[-1]) == "Commit\n" or str(param[-1]) == "Abort\n"):
            self.file.write(" Do not need to recover")
            return True
        action = param[1]
        if action == "put":
            self.file.write(" recover put function")
            #self.cur.execute('INSERT INTO Info VALUES(? , ?)', (param[2], param[3]))
        elif action == "get":
            self.file.write(" recover get function")
            self.cur.execute('SELECT value FROM Info WHERE KEY = ?', param[2])
        elif action == "del":
            self.file.write(" recover del function")
            self.cur.execute('DELETE FROM Info WHERE KEY = ?', param[2])

        self.conn.commit()
        self.file = open(self.name + ".log", "a+")
        self.file.write(" Commit\n")
        self.file.flush()
        self.isRecover = 0
        return 1


    def par_get(self, key):
        ret = ""
        print self.name
        self.file = open(self.name+'.log', 'a+')
        self.file.write(" get "+key)
        self.file.flush()
        try:
            self.cur.execute('SELECT value FROM Info WHERE key = ?', key)
            ret = self.cur.fetchone()
        except Exception, e:
            print e.args
        return str(ret)

    def par_put(self, key, value):
        flag = self.par_decide(key)
        if int(key) != 1:
            self.file = open(self.name + '.log', 'a+')
            self.file.write(" put " + key + " "+ value)
            if flag == True and int(key)!=2:
                try:
                    self.cur.execute('INSERT OR REPLACE INTO Info VALUES(?,?)', (key, value))
                    self.file.write(key)
                except lite.Error, e:
                    print e.args
                return True
            else:
                self.isRecover = 1
                return self.isRecover
        else:
            return False

    def par_del(self, key):

        flag = self.par_decide(key)
        if int(key) != 1:
            self.file = open(self.name + '.log', 'a+')
            self.file.write(" del " + key)
            self.file.flush()
            if flag == True and int(key) != 2:
                try:
                    self.cur.execute('DELETE FROM Info WHERE key = ?', key)
                except Exception, e:
                    print e.args
                return True
            else:
                return False
        else:
            return False

    def par_decide(self, key):
        if int(key) == 1:
            return False
        elif int(key) == 2:
            return True
        else:
            return True

    def par_commit(self):
        try:
            self.conn.commit()
        except lite.Error, e:
            print e.args
        self.file = open(self.name + ".log", "a+")
        self.file.write(" Commit ")
        self.file.flush()
        return True

    def par_abort(self):
        self.file = open(self.name + ".log", "a+")
        self.file.write(" Abort ")
        self.file.flush()
        return True

def main():
    try:
        port = int(sys.argv[1]) #5001
        pid = str(sys.argv[2]) #"1"
        server = SimpleXMLRPCServer(("localhost", port))
        print("listen")
        participant = Participant(('participant'+pid), port) #pid, port
        server.register_instance(participant)
        server.serve_forever()
    except Exception,e:
        print e.args

if __name__ == '__main__':
    main()