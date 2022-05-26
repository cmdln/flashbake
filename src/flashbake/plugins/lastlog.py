from flashbake.plugins import AbstractMessagePlugin
import subprocess
import datetime

class LastLog(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec)

    def addcontext(self, message_file, config):
        llog = self.checklog()
        target = ":"
        ''' loop through llog and store a list of lists that contain a
        colon to the variable x.'''
        x = [s for s in llog for i in s if target in i] 
        
        #for i in range(len(x)):
        #    message_file.write("{0} {1} {2} {3} {4} {5}\n".format(x[i][0], x[i][3], x[i][4], x[i][5], x[i][8], x[i][6]))
        #for i in x:
        #    print(i[8]) 
        for i in x:
            date_placement = [i[3], i[4], i[5], i[6], i[8]]
            y = ' '.join(date_placement)
            #print(date_placement)
            past24 = datetime.datetime.now() - datetime.timedelta(hours=24)
            #if datetime.datetime(*date_placement[2:4]) <= past24:
            #    print(i)
            if datetime.datetime.strptime(y, "%a %b %d %H:%M:%S %Y") >= past24:
            #    print(i)
                message_file.write(f'Most recent lastlog entries: \n{i[0]} {i[3]} {i[4]} {i[5]} {i[6]} {i[8]}')
    def checklog(self):
        last = subprocess.run(["lastlog"], capture_output=True,
                text=True).stdout.strip("\n")
        llog = []
        for line in last.splitlines()[1:]:
            x = line.split()
            llog.append(x)
        return llog
        
