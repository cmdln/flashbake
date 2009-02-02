#
#  commit-wrapper.py
#  Parses a project's control file and wraps git operations, calling the context
#  script to build automatic commit messages as needed.
#
#  Created by Thomas Gideon (cmdln@thecommandline.net) on 1/25/2009
#  Provided as-is, with no warranties
#  License: http://creativecommons.org/licenses/by-nc-sa/3.0/us/ 

import os
import sys
import re
# this import is only valid for Linux
import commands

def go(project_dir):
    os.chdir(project_dir)
    control_file = open('.control', 'r')
    git_status = commands.getoutput('git status')
    pending_re = re.compile('#\s*(renamed|copied|modified):.*')
    for line in git_status.splitlines():
        if pending_re.match(line):
            print line
    try:
        for line in control_file:
            print line
    finally:
        control_file.close()

# call go() when this module is executed as the main script
if __name__ == "__main__":
    project_dir = sys.argv[1]
    go(project_dir)
