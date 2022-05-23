from flashbake.plugins import AbstractMessagePlugin
import subprocess

class LastLog(AbstractMessagePlugin):
    def __init__(self, plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec)

    def addcontext(self, message_file, config):
        llog = self.checklog()
        target = ":"
        ''' loop through llog and store a list of lists that contain a
        colon to the variable x.'''
        x = [s for s in llog for i in s if target in i] 
        
        for i in range(len(x)):
            message_file.write("{0} {1} {2} {3} {4} {5}\n".format(x[i][0], x[i][3], x[i][4], x[i][5], x[i][8], x[i][6]))
    
    def checklog(self):
        last = subprocess.run(["lastlog"], capture_output=True,
                text=True).stdout.strip("\n")
        llog = []
        for line in last.splitlines()[1:]:
            x = line.split()
            llog.append(x)
        return llog
        
