#
#  git.py
#  Wrap the call outs to git, adding sanity checks and environment set up if
#  needed.

import os
import logging
import subprocess

def check_git():
    path_env = os.getenv('PATH')
    if path_env.find(';') > 0:
        path_tokens = path_env.split(';')
    elif path_env.find(':') > 0:
        path_tokens = path_env.split(':')
    else:
        return false
    logging.debug(path_env)

def git(cmd, files=None):
    cmds = list()
    cmds.append('git')
    cmds.append(cmd)
    if files != None:
        cmds += files
    new_env = dict()
    new_env.update(os.environ)
    new_path = new_env['PATH']
    new_path = '/opt/local/bin:%s' % new_path
    new_env['PATH'] = new_path
    output = subprocess.Popen(cmds, stdout=subprocess.PIPE, env=new_env).communicate()[0]
    logging.debug(output)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
            format='%(message)s')
    check_git()
    os.chdir('../foo')
    git('status')
