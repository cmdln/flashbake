#!/usr/bin/env python

'''  flashbake - wrapper script that will get installed by setup.py into the execution path '''

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


from flashbake import commit, context, control
from flashbake.plugins import PluginError, PLUGIN_ERRORS
from optparse import OptionParser
from os.path import join, realpath
import flashbake.git
import fnmatch
import logging
import os.path
import subprocess
import sys



VERSION = '0.26.1'
pattern = '.flashbake'

def main():
    ''' Entry point used by the setup.py installation script. '''
    # handle options and arguments
    parser = _build_parser()

    (options, args) = parser.parse_args()

    if options.quiet and options.verbose:
        parser.error('Cannot specify both verbose and quiet')

    # configure logging
    level = logging.INFO
    if options.verbose:
        level = logging.DEBUG

    if options.quiet:
        level = logging.ERROR

    logging.basicConfig(level=level,
            format='%(message)s')

    home_dir = os.path.expanduser('~')

    # look for plugin directory
    _load_plugin_dirs(options, home_dir)

    if len(args) < 1:
        parser.error('Must specify project directory.')
        sys.exit(1)

    project_dir = args[0]

    # look for user's default control file
    hot_files, control_config = _load_user_control(home_dir, project_dir, options)

    # look for project control file
    control_file = _find_control(parser, project_dir)
    if None == control_file:
        sys.exit(1)

    # emit the context message and exit
    if options.context_only:
        sys.exit(_context_only(options, project_dir, control_file, control_config, hot_files))

    quiet_period = 0
    if len(args) == 2:
        try:
            quiet_period = int(args[1])
        except:
            parser.error('Quiet minutes, "%s", must be a valid number.' % args[1])
            sys.exit(1)

    try:
        (hot_files, control_config) = control.parse_control(project_dir, control_file, control_config, hot_files)
        control_config.context_only = options.context_only
        control_config.dry_run = options.dryrun
        (hot_files, control_config) = control.prepare_control(hot_files, control_config)
        if options.purge:
            commit.purge(control_config, hot_files)
        else:
            commit.commit(control_config, hot_files, quiet_period)
    except (flashbake.git.VCError, flashbake.ConfigError), error:
        logging.error('Error: %s' % str(error))
        sys.exit(1)
    except PluginError, error:
        _handle_bad_plugin(error)
        sys.exit(1)


def multiple_projects():
    usage = "usage: %prog [options] <search_root> [quiet_min]"
    parser = OptionParser(usage=usage, version='%s %s' % ('%prog', VERSION))
    parser.add_option('-o', '--options', dest='flashbake_options', default='',
                      action='store', type='string', metavar='FLASHBAKE_OPTS',
                      help="options to pass through to the 'flashbake' command. Use quotes to pass multiple arguments.")

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error('Must specify root search directory.')
        sys.exit(1)

    LAUNCH_DIR = os.path.abspath(sys.path[0])
    flashbake_cmd = os.path.join(LAUNCH_DIR, "flashbake")
    flashbake_opts = options.flashbake_options.split()
    for project in _locate_projects(args[0]):
        print(project + ":")
        proc = [ flashbake_cmd ] + flashbake_opts + [project]
        if len(args) > 1:
            proc.append(args[1])
        subprocess.call(proc)


def _locate_projects(root):
    for path, dirs, files in os.walk(root): #@UnusedVariable
        for project_path in [os.path.normpath(path) for filename in files if fnmatch.fnmatch(filename, pattern)]:
            yield project_path


def _build_parser():
    usage = "usage: %prog [options] <project_dir> [quiet_min]"

    parser = OptionParser(usage=usage, version='%s %s' % ('%prog', VERSION))
    parser.add_option('-c', '--context', dest='context_only',
            action='store_true', default=False,
            help='just generate and show the commit message, don\'t check for changes')
    parser.add_option('-v', '--verbose', dest='verbose',
            action='store_true', default=False,
            help='include debug information in the output')
    parser.add_option('-q', '--quiet', dest='quiet',
            action='store_true', default=False,
            help='disable all output excepts errors')
    parser.add_option('-d', '--dryrun', dest='dryrun',
            action='store_true', default=False,
            help='execute a dry run')
    parser.add_option('-p', '--plugins', dest='plugin_dir',
            action='store', type='string', metavar='PLUGIN_DIR',
            help='specify an additional location for plugins')
    parser.add_option('-r', '--purge', dest='purge',
            action='store_true', default=False,
            help='purge any files that have been deleted from source control')
    return parser


def _load_plugin_dirs(options, home_dir):
    plugin_dir = join(home_dir, '.flashbake', 'plugins')
    if os.path.exists(plugin_dir):
        real_plugin_dir = realpath(plugin_dir)
        logging.debug('3rd party plugin directory exists, adding: %s' % real_plugin_dir)
        sys.path.insert(0, real_plugin_dir)
    else:
        logging.debug('3rd party plugin directory doesn\'t exist, skipping.')
        logging.debug('Only stock plugins will be available.')

    if options.plugin_dir != None:
        if os.path.exists(options.plugin_dir):
            logging.debug('Adding plugin directory, %s.' % options.plugin_dir)
            sys.path.insert(0, realpath(options.plugin_dir))
        else:
            logging.warn('Plugin directory, %s, doesn\'t exist.' % options.plugin_dir)



def _load_user_control(home_dir, project_dir, options):
    control_file = join(home_dir, '.flashbake', 'config')
    if os.path.exists(control_file):
        (hot_files, control_config) = control.parse_control(project_dir, control_file)
        control_config.context_only = options.context_only
    else:
        hot_files = None
        control_config = None
    return hot_files, control_config


def _find_control(parser, project_dir):
    control_file = join(project_dir, '.flashbake')

    # look for .control for backwards compatibility
    if not os.path.exists(control_file):
        control_file = join(project_dir, '.control')

    if not os.path.exists(control_file):
        parser.error('Could not find .flashbake or .control file in directory, "%s".' % project_dir)
        return None
    else:
        return control_file


def _context_only(options, project_dir, control_file, control_config, hot_files):
    try:
        (hot_files, control_config) = control.parse_control(project_dir, control_file, control_config, hot_files)
        control_config.context_only = options.context_only
        (hot_files, control_config) = control.prepare_control(hot_files, control_config)

        msg_filename = context.buildmessagefile(control_config)
        message_file = open(msg_filename, 'r')

        try:
            for line in message_file:
                print line.strip()
        finally:
            message_file.close()
            os.remove(msg_filename)
        return 0
    except (flashbake.git.VCError, flashbake.ConfigError), error:
        logging.error('Error: %s' % str(error))
        return 1
    except PluginError, error:
        _handle_bad_plugin(error)
        return 1


def _handle_bad_plugin(plugin_error):
    logging.debug('Plugin error, %s.' % plugin_error)
    if plugin_error.reason == PLUGIN_ERRORS.unknown_plugin or plugin_error.reason == PLUGIN_ERRORS.invalid_plugin: #@UndefinedVariable
        logging.error('Cannot load plugin, %s.' % plugin_error.plugin_spec)
        return

    if plugin_error.reason == PLUGIN_ERRORS.missing_attribute: #@UndefinedVariable
        logging.error('Plugin, %s, doesn\'t have the needed plugin attribute, %s.' \
                % (plugin_error.plugin_spec, plugin_error.name))
        return

    if plugin_error.reason == PLUGIN_ERRORS.invalid_attribute: #@UndefinedVariable
        logging.error('Plugin, %s, has an invalid plugin attribute, %s.' \
                % (plugin_error.plugin_spec, plugin_error.name))
        return

    if plugin_error.reason == PLUGIN_ERRORS.missing_property:
        logging.error('Plugin, %s, requires the config option, %s, but it was missing.' \
                % (plugin_error.plugin_spec, plugin_error.name))
        return
