#
#  git.py
#  Wrap the call outs to git, adding sanity checks and environment set up if
#  needed.

import os
import logging
import subprocess

class VCError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Git():
    def __init__(self, git_path=None):
        path_env = os.getenv('PATH')
        if path_env.find(';') > 0:
            path_sep = ';'
            path_tokens = path_env.split(';')
        elif path_env.find(':') > 0:
            path_sep = ':'
            path_tokens = path_env.split(':')
        else:
            raise VCError('Could not parse PATH env var, %s' % path_env)
        git_exists = False
        for path_token in path_tokens:
            if os.path.exists(os.path.join(path_token, 'git')):
                git_exists = True
        if not git_exists and git_path != None:
            if os.path.exists(os.path.join(git_path, 'git')):
                git_exists = True
        if not git_exists:
            raise VCError('Could not find git executable on PATH.')
        self.__init_env(path_sep, git_path)

    def run(self, cmd, files=None):
        cmds = list()
        cmds.append('git')
        cmds.append(cmd)
        if files != None:
            cmds += files
        output = subprocess.Popen(cmds, stdout=subprocess.PIPE, env=self.env).communicate()[0]
        logging.debug(output)

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
    os.chdir('../foo')
    git.run('status')
