#!/usr/bin/env python
#
#  commit-wrapper.py
#  Parses a project's control file and wraps git operations, calling the context
#  script to build automatic commit messages as needed.
#
#  version 0.14 - packaging and install
#
#  history:
#  version 0.13 - code clean up
#  version 0.12 - added error checks to network calls
#  version 0.11 - use a regex to fix trailing tweedle causing false reports
#  version 0.10 - added link check, added logic to add files
#  version 0.9 - added a trap for a fatal error from git
#  version 0.8 - more logging changes
#  version 0.7 - more logging changes
#  version 0.6 - improved logging, more quoting of arguments to shell
#  version 0.5 - consolidate commits
#  version 0.4 - Added quotes to git call for filenames with spaces
#  version 0.3 - SMTP port, she-bang
#  version 0.2 - email notification
#  version 0.1 - git functionality complete
#
#  Created by Thomas Gideon (cmdln@thecommandline.net) on 1/25/2009
#  Provided as-is, with no warranties
#  License: http://creativecommons.org/licenses/by-nc-sa/3.0/us/ 

import sys
from flashbake.commit import commit

# just provide the command line hook into the flashbake.commit module
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "%s <project directory> <quiet period>" % sys.argv[0]
        sys.exit(1)

    project_dir = sys.argv[1]
    quiet_period = int(sys.argv[2])
    print 'flashbake version 0.14'
    commit(project_dir, quiet_period)
