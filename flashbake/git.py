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
    def __init__(self, git_path=None):
        # look for git in the environment's PATH var
        path_env = os.getenv('PATH')
        if path_env.find(';') > 0:
            path_sep = ';'
            path_tokens = path_env.split(';')
        elif path_env.find(':') > 0:
            path_sep = ':'
            path_tokens = path_env.split(':')
        else:
            # not sure how else to split out the PATH or if there is an OS
            # agnostic way to do this
            raise VCError('Could not parse PATH env var, %s' % path_env)
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
        self.__init_env(path_sep, git_path)

    def status(self):
        """ Get the git status for the specified files, or the entire current
            directory. """
        return self.__run('status')

    def __run(self, cmd, files=None):
        cmds = list()
        cmds.append('git')
        cmds.append(cmd)
        if files != None:
            cmds += files
        return subprocess.Popen(cmds, stdout=subprocess.PIPE, env=self.env).communicate()[0]

    def __init_env(self, path_sep, git_path):
        self.env = dict()
        self.env.update(os.environ)
        if git_path != None:
            new_path = self.env['PATH']
            new_path = '%s%s%s' % (git_path, path_sep, new_path)
            self.env['PATH'] = new_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
            format='%(message)s')
    git = Git('/opt/local/bin')
    try:
        git = Git()
    except VCError, e:
        logging.info(e)
    os.chdir('../foo')
    logging.info(git.status())
