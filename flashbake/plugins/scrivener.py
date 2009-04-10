# scrivener.py -- Scrivener flashbake plugin
# by Jason Penney, jasonpenney.net

import logging, flashbake, flashbake.plugins, fnmatch, os
import subprocess, glob
import pickle
from flashbake.plugins import *



## find_executable and executable_available could possibly be useful elsewhere
def find_executable(executable):
    found = filter(lambda ex: os.path.exists(ex),
                   map(lambda path_token:
                       os.path.join(path_token,executable),
                       os.getenv('PATH').split(os.pathsep)))
    if (len(found) == 0):
        return None
    return found[0]

def executable_available(executable):
    return find_executable(executable) != None

    
def find_scrivener_projects(hot_files):
    files=list()
    for f in hot_files.control_files:
        if fnmatch.fnmatch(f,'*.scriv'):
            files.append(f)

    return files

def find_scrivener_project_contents(hot_files, scrivener_project):
    contents=list()
    for path, dirs, files in os.walk(os.path.join(hot_files.project_dir,scrivener_project)):
        relpath = os.path.relpath(path,hot_files.project_dir)
        for filename in files:
            contents.append(os.path.join(relpath,filename))

    return contents

def get_logfile_name(scriv_proj_dir):
    return os.path.join(os.path.dirname(scriv_proj_dir),
                        ".%s.flashbake.wordcount" % os.path.basename(scriv_proj_dir))


## TODO: deal with deleted files
class ScrivenerFile(AbstractFilePlugin):
    
    def __init__(self, plugin_spec):
        AbstractFilePlugin.__init__(self, plugin_spec)

    def init(self,config):
        config.sharedproperty('scrivener_projects')
        
    def processfiles(self, hot_files, config):
        if 'scrivener_projects' in config.__dict__:
            scrivener_projects = config.scrivener_projects
        else:
            scrivener_projects = find_scrivener_projects(hot_files)
            config.scrivener_projects = scrivener_projects
            
        for f in scrivener_projects:
            logging.debug("ScrivenerFile: adding '%s'" % f)
            for hotfile in find_scrivener_project_contents(hot_files,f):
                #logging.debug(" - %s" % hotfile)
                hot_files.control_files.add(hotfile)

 
        

class ScrivenerWordcountFile(AbstractFilePlugin):
    """ Record Wordcount for Scrivener Files """
    def __init__(self, plugin_spec):
        AbstractFilePlugin.__init__(self, plugin_spec)

    #def init(self, config):
        # TODO: need a way to gracefully skip plugin in this case
        # if not executable_available('textutil')
        #    raise PluginError(PLUGIN_ERRORS.missing_property, self.plugin_spec, "textutilcmd")

    def init(self,config):
        config.sharedproperty('scrivener_projects')
        config.sharedproperty('scrivener_project_count')
        
    def processfiles(self, hot_files, config):
        if 'scrivener_projects' in config.__dict__:
            scrivener_projects = config.scrivener_projects
        else:
            scrivener_projects = find_scrivener_projects(hot_files)
            config.scrivener_projects = scrivener_projects

        config.scrivener_project_count = dict()
        for f in scrivener_projects:
            scriv_proj_dir  = os.path.join(hot_files.project_dir,f)
            hot_logfile = get_logfile_name(f)
            logfile = os.path.join(hot_files.project_dir,hot_logfile)

            if os.path.exists(logfile):
                logging.debug("logifile exists %s" % logfile)
                log = open(logfile,'r')
                oldCount = pickle.load(log)
                log.close()
            else:
                oldCount = {
                    'Content': 0,
                    'Synopsis': 0,
                    'Notes' : 0,
                    'All' :0
                    }

            newCount = {
                'Content': self.get_count(scriv_proj_dir, ["*[0-9].rtfd"]),
                'Synopsis': self.get_count(scriv_proj_dir, ['*_synopsis.txt' ]),
                'Notes': self.get_count(scriv_proj_dir, [ '*_notes.rtfd' ]),
                'All':  self.get_count(scriv_proj_dir, ['*.rtfd','*.txt'])
                }

            config.scrivener_project_count[f] = { 'old': oldCount, 'new': newCount }
            if not config.context_only:
                log = open(logfile,'w')
                pickle.dump(config.scrivener_project_count[f]['new'],log)
                log.close()
                if not hot_logfile in hot_files.control_files:
                    hot_files.control_files.add(logfile)



    def get_count(self,file,matches):
        count = 0
        args = ['textutil','-stdout','-cat', 'txt']
        do_count=False
        for match in list(matches):
            for f in glob.glob(os.path.normpath(os.path.join(file,match))):
                do_count=True
                args.append(f)

        if do_count:
            p = subprocess.Popen(args, stdout=subprocess.PIPE,
                             close_fds = True)

            for line in p.stdout:
                count += len(line.split(None))
        return count
    
class ScrivenerWordcountMessage(AbstractMessagePlugin):
    """ Display Wordcount for Scrivener Files """

    def __init__(self,plugin_spec):
        AbstractMessagePlugin.__init__(self, plugin_spec, False)
        
    def init(self, config):
        config.sharedproperty('scrivener_project_counts')

    def addcontext(self, message_file, config):
        to_file = ''
        if 'scrivener_project_count' in config.__dict__:
            for proj in config.scrivener_project_count:
                to_file += "Wordcount: %s\n" % proj
                for key in [ 'Content', 'Synopsis', 'Notes', 'All' ]:
                    new = config.scrivener_project_count[proj]['new'][key]
                    old = config.scrivener_project_count[proj]['old'][key]
                    diff = new - old
                    to_file += "- " + key.ljust(10,' ') + str(new).rjust(20)
                    if diff != 0:
                        to_file += " (%+d)" % (new - old)
                    to_file +="\n"

            message_file.write(to_file)        

        

