'''
Created on Aug 3, 2009

control.py - control file parsing and preparation.

@author: cmdln
'''
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
import flashbake
import logging



def parse_control(project_dir, control_file, config=None, results=None):
    """ Parse the dot-control file to get config options and hot files. """

    logging.debug('Checking %s' % control_file)

    if None == results:
        hot_files = flashbake.HotFiles(project_dir)
    else:
        hot_files = results

    if None == config:
        control_config = flashbake.ControlConfig()
    else:
        control_config = config

    control_file = open(control_file, 'r')
    try:
        for line in control_file:
            # skip anything else if the config consumed the line
            if control_config.capture(line):
                continue

            hot_files.addfile(line.strip())
    finally:
        control_file.close()

    return (hot_files, control_config)

def prepare_control(hot_files, control_config):
    control_config.init()
    logging.debug("loading file plugins")
    for plugin in control_config.file_plugins:
        logging.debug("running plugin %s" % plugin)
        plugin.pre_process(hot_files, control_config)
    return (hot_files, control_config)

