#!/bin/bash

# This is a wrapper for git and commit-context.py to add a bit of intelligence
# to a regular cron job to detect changes but only after a set number of minutes
# (the quiet period) where the files have not been changed and to use the
# python script to build a nice, contextual commit message.
#
#  Create by Thomas Gideon (cmdln@thecommandline.net) on 1/26/2009
#  Provided as-is, with no warranties
#  License: http://creativecommons.org/licenses/by-nc-sa/3.0/us/ 

# capture the script directory so the python script can be run
work_dir=$(dirname $0)
proj_dir=$1

if [ -z $proj_dir ]
then
	echo "Have to provide a project directory!"
    echo "Usage: $0 <project dir> <quiet minutes>"
    exit 1
fi

quiet=$2

if [ -z $quiet ]
then
	echo "Have to provide a minimum number of minutes of no file changes before
committing."
    echo "Usage: $0 <project dir> <quiet minutes>"
    exit 1
fi

# move into the project directory
cd $proj_dir

# see if git is aware of any changes that need committing
git status | grep "Changed but not updated:" > /dev/null

if [ 0 -eq $? ]
then
    # borrowed this idea from continuous integration, previous commits when
    # files are actively being worked on, helps smooth out the history
    within_n=$(find . -mmin -$2 -print | grep -v "^\.$" | grep -v ".git")

	if [ -z $within_n ]
	then
        echo "Pending files in $1 to commit!"
		python $work_dir/commit-context.py | git commit -a -F - 
    else
        echo "Changes were too recent, waiting."
	fi
else
    echo "No changes to commit."
fi

