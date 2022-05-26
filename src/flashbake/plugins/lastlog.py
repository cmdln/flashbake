from flashbake.plugins import AbstractMessagePlugin
import subprocess
import datetime

class LastLog(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec)
        self.define_property('interval', int, required=False)

    def addcontext(self, message_file, config):
        llog = self.checklog()
        target = ":"
        ''' loop through llog and store a list of lists that contain a
        colon to the variable x.'''
        x = [s for s in llog for i in s if target in i] 
        if self.interval == None:
            self.interval = 24
        for i in x:
            date_placement = [i[3], i[4], i[5], i[6], i[8]]
            y = ' '.join(date_placement)
            past24 = datetime.datetime.now() - datetime.timedelta(hours=self.interval)
            if datetime.datetime.strptime(y, "%a %b %d %H:%M:%S %Y") >= past24:
                message_file.write(f'Most recent lastlog entries: \n{i[0]} {i[3]} {i[4]} {i[5]} {i[6]} {i[8]}')
    def checklog(self):
        ''' Get the lastlog and turn each line into a list of lists. '''
        last = subprocess.run(["lastlog"], capture_output=True,
                text=True).stdout.strip("\n")
        llog = []
        for line in last.splitlines()[1:]:
            x = line.split()
            llog.append(x)
        return llog
        
