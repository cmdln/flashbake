from flashbake.plugins import AbstractMessagePlugin
import subprocess
import datetime

class LastLog(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec)
        self.define_property('period', int, required=False)

    def addcontext(self, message_file, config):
        llog = self.checklog()
        target = ":"
        ''' loop through the lists in the llog variable, and store in the 
        x variable any of the lists that contain a colon.'''
        x = [s for s in llog for i in s if target in i]
        ''' set the period to check the last log to the last 24 hours
        unless the period is set by the user. '''
        if self.period == None:
            self.period = 24
        ''' take the date in each list in variable x, and see if they are equal
        to or newer than the specified period. Then write the relevant log
        entries to the commit message. '''
        for i in x:
            date_placement = [i[3], i[4], i[5], i[6], i[8]]
            y = ' '.join(date_placement)
            past24 = datetime.datetime.now() - datetime.timedelta(hours=self.period)
            if datetime.datetime.strptime(y, "%a %b %d %H:%M:%S %Y") >= past24:
                message_file.write(f'Most recent lastlog entries: \n{i[0]} {i[3]} {i[4]} {i[5]} {i[6]} {i[8]}\n')
    def checklog(self):
        ''' Get the lastlog and turn each line of the log into a list. '''
        last = subprocess.run(["lastlog"], capture_output=True,
                text=True).stdout.strip("\n")
        llog = []
        for line in last.splitlines()[1:]:
            x = line.split()
            llog.append(x)
        return llog
        
