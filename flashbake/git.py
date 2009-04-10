#
#  git.py
#  Wrap the call outs to git, adding sanity checks and environment set up if
#  needed.

import os
import logging
import subprocess

class VCError(Exception):
    """ Error when the version control wrapper object cannot be set up. """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Git():
    def __init__(self, cwd, git_path=None):
        # look for git in the environment's PATH var
        path_env = os.getenv('PATH')
        if (len(path_env) == 0):
            path_env = os.defpath
        path_tokens = path_env.split(os.pathsep)
        git_exists = False
        # if there is a git_path option, that takes precedence
        if git_path != None:
            if git_path.endswith('git'):
                git_path = os.path.dirname(git_path)
            if os.path.exists(os.path.join(git_path, 'git')):
                git_exists = True
        else:
            for path_token in path_tokens:
                if os.path.exists(os.path.join(path_token, 'git')):
                    git_exists = True
        # fail much sooner and more quickly then if git calls are made later,
        # naively assuming it is available
        if not git_exists:
            raise VCError('Could not find git executable on PATH.')
        # set up an environment mapping suitable for use with the subprocess
        # module
        self.__init_env(git_path)
        self.__cwd = cwd

    def status(self, filename=None):
        """ Get the git status for the specified files, or the entire current
            directory. """
        if filename != None:
            files = list()
            files.append(filename)
            return self.__run('status', files=files)
        else:
            return self.__run('status')

    def add(self, file):
        """ Add an unknown but existing file. """
        files = [ file ]
        return self.__run('add', files=files)

    def commit(self, messagefile, files):
        """ Commit a list of files, the files should be strings and quoted. """
        options = ['-F', messagefile]
        return self.__run('commit', options, files)

    def __run(self, cmd, options=None, files=None):
        cmds = list()
        cmds.append('git')
        cmds.append(cmd)
        if options != None:
            cmds += options
        if files != None:
            cmds += files
        proc = subprocess.Popen(cmds, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, cwd=self.__cwd, env=self.env)
        return proc.communicate()[0]

    def __init_env(self, git_path):
        self.env = dict()
        self.env.update(os.environ)
        if git_path != None:
            new_path = self.env['PATH']
            new_path = '%s%s%s' % (git_path, os.pathsep, new_path)
            self.env['PATH'] = new_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
            format='%(message)s')
    git = Git('../foo', '/opt/local/bin')
    try:
        git = Git('../foo')
    except VCError, e:
        logging.info(e)
    os.chdir('../foo')
    logging.info(git.status())
