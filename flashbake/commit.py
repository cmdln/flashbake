#!/usr/bin/env python
#
#  commit.py
#  Parses a project's control file and wraps git operations, calling the context
#  script to build automatic commit messages as needed.
#
#  Created by Thomas Gideon (cmdln@thecommandline.net) on 1/25/2009
#  Provided as-is, with no warranties
#  License: http://creativecommons.org/licenses/by-nc-sa/3.0/us/ 

import os
import sys
import re
import datetime
import time
import logging
import context
# this import is only valid for Linux
import commands
# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.mime.text import MIMEText
from flashbake import ControlConfig, ParseResults

def parsecontrol(project_dir, control_file):
    """ Parse the dot-control file in the project directory. """

    logging.debug('Checking %s' % project_dir)
    # change to the project directory, necessary to find the .flashbake file and
    # to correctly refer to the project files by relative paths
    os.chdir(project_dir)
    # read the control file into a hashable set to compare git status entries
    # more easily against the possible subset that should be controlled by the
    # script
    control_file = open(control_file, 'r')
    parse_results = ParseResults()
    control_config = ControlConfig()
    try:
        for line in control_file:
            # skip anything else if the config consumed the line
            if __capture(control_config, line):
                continue

            parse_results.addfile(line.strip())
    finally:
        control_file.close()

    control_config.init()

    return (parse_results, control_config)

def commit(project_dir, control_file, quiet_mins, dryrun):
    (parse_results, control_config) = parsecontrol(project_dir, control_file)
    control_config.dryrun = dryrun

    # get the git status for the project
    git_status = commands.getoutput('git status')

    if git_status.startswith('fatal'):
        logging.error('Fatal error from git.')
        logging.error(git_status)
        sys.exit(1)

    # in particular find the existing entries that need a commit
    pending_re = re.compile('#\s*(renamed|copied|modified|new file):.*')

    now = datetime.datetime.today()
    quiet_period = datetime.timedelta(minutes=quiet_mins)

    git_commit = 'git commit -F %(msg_filename)s %(filenames)s'
    file_template = ' "%s"'
    to_commit = ''
    # first look in the files git already knows about
    for line in git_status.splitlines():
        if pending_re.match(line):
            pending_file = __trimgit(line)

            # not in the dot-control file, skip it
            if not (parse_results.contains(pending_file)):
                continue

            logging.debug('Parsing status line %s to determine commit action' % line)

            # remove files that will be considered for commit
            parse_results.remove(pending_file)

            # check the quiet period against mtime
            last_mod = os.path.getmtime(pending_file)
            pending_mod = datetime.datetime.fromtimestamp(last_mod)
            pending_mod += quiet_period

            # add the file to the list to include in the commit
            if pending_mod < now:
                to_commit += file_template % pending_file
                logging.debug('Flagging file, %s, for commit.' % pending_file)
            else:
                logging.debug('Change for file, %s, is too recent.' % pending_file)

    logging.debug('\nExamining unknown files.')

    parse_results.warnlinks()

    # figure out what the status of the remaining files is
    git_status = 'git status "%s"'
    for control_file in parse_results.control_files:
        if not os.path.exists(control_file):
            logging.debug('%s does not exist yet.' % control_file)
            parse_results.putabsent(control_file)
            continue

        status_output = commands.getoutput(git_status % control_file)

        if status_output.startswith('error'):
            if status_output.find('did not match') > 0:
                parse_results.putneedsadd(control_file)
                logging.debug('%s exists but is unknown by git.' % control_file)
            else:
                logging.error('Unknown error occurred!')
                logging.error(status_output)
            continue
        # use a regex to match so we can enforce whole word rather than
        # substring matchs, otherwise 'foo.txt~' causes a false report of an
        # error
        control_re = re.compile('\<' + re.escape(control_file) + '\>')
        if control_re.search(status_output) == None:
            logging.debug('%s has no uncommitted changes.' % control_file)
        # if anything hits this block, we need to figure out why
        else:
            logging.error('%s is in the status message but failed other tests.' % control_file)
            logging.error('Try \'git status "%s"\' for more info.' % control_file)

    parse_results.addorphans(control_config)

    if len(to_commit.strip()) > 0:
        logging.info('Committing changes to known files, %s.' % to_commit)
        message_file = context.buildmessagefile(control_config)
        # consolidate the commit to be friendly to how git normally works
        git_commit = git_commit % {'msg_filename' : message_file, 'filenames' : to_commit}
        logging.debug(git_commit)
        if not dryrun:
            commit_output = commands.getoutput(git_commit)
            logging.debug(commit_output)
        os.remove(message_file)
        logging.info('Commit for known files complete.')
    else:
        logging.info('No changes to known files found to commit.')

    if parse_results.needsnotice():
        __sendnotice(control_config, project_dir, parse_results)
    else:
        logging.info('No missing or untracked files found, not sending email notice.')
        
def __capture(config, line):
    """ Used by the dot-control parsing code to capture files and properties
        as they are encountered. """
    # grab comments but don't do anything
    if line.startswith('#'):
        return True

    # grab blanks but don't do anything
    if len(line.strip()) == 0:
        return True

    if line.find(':') > 0:
        prop_tokens = line.split(':', 1)
        prop_name = prop_tokens[0].strip()
        prop_value = prop_tokens[1].strip()

        if 'plugins' == prop_name:
           config.addplugins(prop_value.split(','))
           return True

        if prop_name in config.int_props:
            prop_value = int(prop_value)

        # hang onto any extra propeties in case plugins use them
        if not prop_name in config.__dict__:
            config.extra_props[prop_name] = prop_value;
            return True

        config.__dict__[prop_name] = prop_value

        return True

    return False

def __trimgit(status_line):
    if status_line.find('->') >= 0:
        tokens = status_line.split('->')
        return tokens[1].strip()

    tokens = status_line.split(':')
    return tokens[1].strip()

def __sendnotice(control_config, project_dir, parse_results):
    if None == control_config.notice_to:
        logging.info('Skipping notice, no notice_to: recipient set.')
        return

    body = ''
    
    if len(parse_results.not_exists) > 0:
        body += '\nThe following files do not exist:\n\n'

        for file in parse_results.not_exists:
           body += '\t' + file + '\n'

        body += '\nMake sure there is not a typo in .control and that you created/saved the file.\n'
    
    if len(parse_results.linked_files) > 0:
        body += '\nThe following files in .control are links or have a link in their directory path.\n'

        for (file, link) in parse_results.linked_files.iteritems():
            if file == link:
                body += '\t' + file + ' is a link\n'
            else:
                body += '\t' + link + ' is a link on the way to ' + file + '\n'

        body += '\nMake sure the physical file and its parent directories reside in the git project directory.\n'


    if control_config.dryrun:
        logging.debug(body)
        logging.info('Dry run, skipping email notice.')
        return

    # Create a text/plain message
    msg = MIMEText(body, 'plain')

    msg['Subject'] = 'Some files in %s do not exist' % project_dir
    msg['From'] = control_config.notice_from
    msg['To'] = control_config.notice_to

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    logging.debug('\nConnecting to SMTP port %d' % control_config.smtp_port)

    try:
        s = smtplib.SMTP()
        s.connect(port=control_config.smtp_port)
        logging.info('Sending notice to %s.' % control_config.notice_to)
        logging.debug(body)
        s.sendmail(control_config.notice_from, [control_config.notice_to], msg.as_string())
        logging.info('Notice sent.')
        s.close()
    except:
        logging.error('Couldn\'t connect, will send later.')
