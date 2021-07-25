#    copyright 2009 Thomas Gideon
#
#    This file is part of flashbake.
#
#    flashbake is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    flashbake is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with flashbake.  If not, see <http://www.gnu.org/licenses/>.

'''  commit.py - Parses a project's control file and wraps git operations, calling the context
script to build automatic commit messages as needed.'''

from flashbake import context, git
import datetime
import logging
import os
import re
import sys



DELETED_RE = re.compile('#\s*deleted:.*')
# takes the following regular expression pattern and turns it into a 
# regular expression object. This is used to identify deleted files.

def commit(control_config, hot_files, quiet_mins):
    # change to the project directory, necessary to find the .flashbake file and
    # to correctly refer to the project files by relative paths
    os.chdir(hot_files.project_dir)

    git_obj = git.Git(hot_files.project_dir, control_config.git_path)

    # the wrapper object ensures git is on the path
    # get the git status for the project
    git_status = git_obj.status().decode('utf-8')

    _handle_fatal(hot_files, git_status)

    # in particular find the existing entries that need a commit
    # this command is used in `to_commit` on files returned from 
    # `def status` in git.py.
    pending_re = re.compile("\s*(renamed|copied|modified|new file):.*")

    now = datetime.datetime.today()
    quiet_period = datetime.timedelta(minutes=quiet_mins)

    to_commit = list()
    # first look in the files git already knows about
    logging.debug("Examining git status.")
    for line in git_status.splitlines():
        if pending_re.match(line):
            pending_file = _trimgit(line)

            # not in the dot-control file, skip it
            if not (hot_files.contains(pending_file)):
                continue

            logging.debug(f'Parsing status line {line} to determine commit action')

            # remove files that will be considered for commit
            hot_files.remove(pending_file)

            # check the quiet period against mtime
            last_mod = os.path.getmtime(pending_file)
            pending_mod = datetime.datetime.fromtimestamp(last_mod)
            pending_mod += quiet_period

            # add the file to the list to include in the commit
            if pending_mod < now:
                to_commit.append(pending_file)
                logging.debug(f'Flagging file, {pending_file}, for commit.' )
            else:
                logging.debug(f'Change for file, {pending_file}, is too recent.')
        _capture_deleted(hot_files, line)

    logging.debug('Examining unknown or unchanged files.')

    hot_files.warnproblems()

    # figure out what the status of the remaining files is
    for control_file in hot_files.control_files:
        # this shouldn't happen since HotFiles.addfile uses glob.iglob to expand
        # the original file lines which does so based on what is in project_dir
        if not os.path.exists(control_file):
            logging.debug(f'{control_file} does not exist yet.' )
            hot_files.putabsent(control_file)
            continue

        status_output = git_obj.status(control_file).decode('utf-8')

        # needed for git >= 1.7.0.4
        if status_output.find('Untracked files') > 0:
            if not control_config.dry_run or control_config.context_only:
                hot_files.putneedsadd(control_file)
                continue
        if status_output.startswith('error'):
            # needed for git < 1.7.0.4
            if status_output.find('did not match') > 0:
                hot_files.putneedsadd(control_file)
                logging.debug(f'{control_file} exists but is unknown by git.')
            else:
                logging.error('Unknown error occurred!')
                logging.error(status_output)
            continue
        # use a regex to match so we can enforce whole word rather than
        # substring matchs, otherwise 'foo.txt~' causes a false report of an
        # error
        control_re = re.compile('\<' + re.escape(control_file) + '\>')
        if control_re.search(status_output) == None:
            logging.debug(f'{control_file} has no uncommitted changes.')
        # if anything hits this block, we need to figure out why
        else:
            logging.error(f'{control_file} is in the status message but failed other tests.'  )
            logging.error(f'Try \'git status "{control_file}"\' for more info.')

    hot_files.addorphans(git_obj, control_config)

    for plugin in control_config.file_plugins:
        plugin.post_process(to_commit, hot_files, control_config)

    if len(to_commit) > 0:
        logging.info(f'Committing changes to known files, {to_commit}.' )
        message_file = context.buildmessagefile(control_config)
        if not control_config.dry_run:
            # consolidate the commit to be friendly to how git normally works
            commit_output = git_obj.commit(message_file, to_commit)
            logging.debug(commit_output)
        os.remove(message_file)
        _send_commit_notice(control_config, hot_files, to_commit)
        logging.info('Commit for known files complete.')
    else:
        logging.info('No changes to known files found to commit.')

    if hot_files.needs_warning():
        _send_warning(control_config, hot_files)
    else:
        logging.info('No missing or untracked files found, not sending warning notice.')

def purge(control_config, hot_files):
    # change to the project directory, necessary to find the .flashbake file and
    # to correctly refer to the project files by relative paths
    os.chdir(hot_files.project_dir)

    git_obj = git.Git(hot_files.project_dir, control_config.git_path)

    # the wrapper object ensures git is on the path
    git_status = git_obj.status().decode('utf-8')

    _handle_fatal(hot_files, git_status)

    logging.debug("Examining git status.")
    for line in git_status.splitlines():
        _capture_deleted(hot_files, line)

    if len(hot_files.deleted) > 0:
        logging.info(f'Committing removal of known files, {hot_files.deleted}.' )
        message_file = context.buildmessagefile(control_config)
        if not control_config.dry_run:
            # consolidate the commit to be friendly to how git normally works
            commit_output = git_obj.commit(message_file, hot_files.deleted)
            logging.debug(commit_output)
        os.remove(message_file)
        logging.info('Commit for deleted files complete.')
    else:
        logging.info('No deleted files to purge')


def _capture_deleted(hot_files, line):
    if DELETED_RE.match(line):
        deleted_file = _trimgit(line)
        # remove files that will are known to have been deleted
        hot_files.remove(deleted_file)
        hot_files.put_deleted(deleted_file)


def _handle_fatal(hot_files, git_status):
    if git_status.startswith('fatal'):
        logging.error('Fatal error from git.')
        if git_status.startswith('fatal:'):
            logging.error('Make sure "git init" was run in {}'.format(os.path.realpath(hot_files.project_dir)))
        else:
            logging.error(git_status)
        sys.exit(1)


def _trimgit(status_line):
    if status_line.find('->') >= 0:
        tokens = status_line.decode('utf-8').split('->')
        return tokens[1].strip()

    tokens = status_line.split(':')
    return tokens[1].strip()


def _send_warning(control_config, hot_files):
    if (len(control_config.notify_plugins) == 0
            and not control_config.dry_run):
        logging.info('Skipping notice, no notify plugins configured.')
        return

    for plugin in control_config.notify_plugins:
        plugin.warn(hot_files, control_config)


def _send_commit_notice(control_config, hot_files, to_commit):
    if (len(control_config.notify_plugins) == 0
            and not control_config.dry_run):
        logging.info('Skipping notice, no notify plugins configured.')
        return

    for plugin in control_config.notify_plugins:
        plugin.notify_commit(to_commit, hot_files, control_config)
