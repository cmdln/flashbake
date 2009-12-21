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

'''  __init__.py - Shared classes and functions for the flashbake package.'''

from flashbake.plugins import PluginError, PLUGIN_ERRORS
from types import *
import commands
import flashbake.plugins #@UnresolvedImport
import glob
import logging
import os
import os.path
import re
import sys #@Reimport




class ConfigError(Exception):
    pass


class ControlConfig:
    """ Accumulates options from a control file for use by the core modules as
        well as for the plugins.  Also handles boot strapping the configured
        plugins. """
    def __init__(self):
        self.initialized = False
        self.dry_run = False
        self.extra_props = dict()

        self.prop_types = dict()

        self.plugin_names = list()
        self.msg_plugins = list()
        self.file_plugins = list()
        self.notify_plugins = list()

        self.git_path = None
        self.project_name = None

    def capture(self, line):
        ''' Parse a line from the control file if it is relevant to plugin configuration. '''
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
                self.add_plugins(prop_value.split(','))
                return True

            # hang onto any extra propeties in case plugins use them
            if not prop_name in self.__dict__:
                self.extra_props[prop_name] = prop_value;
                return True

            try:
                if prop_name in self.prop_types:
                    prop_value = self.prop_types[prop_name](prop_value)
                self.__dict__[prop_name] = prop_value
            except:
                raise ConfigError(
                        'The value, %s, for option, %s, could not be parse as %s.'
                        % (prop_value, prop_name, self.prop_types[prop_name]))

            return True

        return False

    def init(self):
        """ Do any property clean up, after parsing but before use """
        if self.initialized == True:
            return

        self.initialized = True

        if len(self.plugin_names) == 0:
            raise ConfigError('No plugins configured!')

        self.share_property('git_path')
        self.share_property('project_name')

        all_plugins = list()
        with_deps = dict()
        for plugin_name in self.plugin_names:
            logging.debug("initalizing plugin: %s" % plugin_name)
            try:
                plugin = self.create_plugin(plugin_name)
                if len(plugin.dependencies()) == 0:
                    all_plugins.append(plugin)
                else:
                    dep = Dependency(plugin)
                    dep.map(with_deps)
                if isinstance(plugin, flashbake.plugins.AbstractMessagePlugin):
                    logging.debug("Message Plugin: %s" % plugin_name)
                    # TODO add notion of dependency for ordering
                    if 'flashbake.plugins.location:Location' == plugin_name:
                        self.msg_plugins.insert(0, plugin)
                    else:
                        self.msg_plugins.append(plugin)
                if isinstance(plugin, flashbake.plugins.AbstractFilePlugin):
                    logging.debug("File Plugin: %s" % plugin_name)
                    self.file_plugins.append(plugin)
                if isinstance(plugin, flashbake.plugins.AbstractNotifyPlugin):
                    logging.debug('Notify Plugin: %s' % plugin_name)
                    self.notify_plugins.append(plugin)
            except PluginError, e:
                # re-raise critical plugin error
                if not e.reason == PLUGIN_ERRORS.ignorable_error: #@UndefinedVariable
                    raise e
                # allow ignorable errors through with a warning
                logging.warning('Skipping plugin, %s, ignorable error: %s' %
                        (plugin_name, e.name))

        for plugin in all_plugins:
            plugin.share_properties(self)
            if plugin.plugin_spec in with_deps:
                for dep in with_deps[plugin.plugin_spec]:
                    dep.satisfy(plugin, all_plugins)

        if len(Dependency.all) > 0:
            logging.error('Unsatisfied dependencies!')

        for plugin in all_plugins:
            plugin.capture_properties(self)
            plugin.init(self)

    def share_property(self, name, type=None):
        """ Declare a shared property, this way multiple plugins can share some
            value through the config object. """
        if name in self.__dict__:
            return

        value = None

        if name in self.extra_props:
            value = self.extra_props[name]
            del self.extra_props[name]

            if type != None:
                try:
                    value = type(value)
                except:
                    raise ConfigError('Problem parsing %s for option %s'
                            % (name, value))

        self.__dict__[name] = value

    def add_plugins(self, plugin_names):
        # use a comprehension to ensure uniqueness
        [self.__add_last(inbound_name) for inbound_name in plugin_names]

    def create_plugin(self, plugin_spec):
        """ Initialize a plugin, including vetting that it meets the correct
            protocol; not private so it can be used in testing. """
        if plugin_spec.find(':') < 0:
            logging.debug('Plugin spec not validly formed, %s.' % plugin_spec)
            raise PluginError(PLUGIN_ERRORS.invalid_plugin, plugin_spec) #@UndefinedVariable

        tokens = plugin_spec.split(':')
        module_name = tokens[0]
        plugin_name = tokens[1]

        try:
            __import__(module_name)
        except ImportError:
            logging.warn('Invalid module, %s' % plugin_name)
            raise PluginError(PLUGIN_ERRORS.unknown_plugin, plugin_spec) #@UndefinedVariable

        try:
            plugin_class = self.__forname(module_name, plugin_name)
            plugin = plugin_class(plugin_spec)
        except Exception, e:
            logging.debug(e)
            logging.debug('Couldn\'t load class %s' % plugin_spec)
            raise PluginError(PLUGIN_ERRORS.unknown_plugin, plugin_spec) #@UndefinedVariable
        is_message_plugin = isinstance(plugin, flashbake.plugins.AbstractMessagePlugin)
        is_file_plugin = isinstance(plugin, flashbake.plugins.AbstractFilePlugin)
        is_notify_plugin = isinstance(plugin, flashbake.plugins.AbstractNotifyPlugin)
        if not is_message_plugin and not is_file_plugin and not is_notify_plugin:
            raise PluginError(PLUGIN_ERRORS.invalid_type, plugin_spec) #@UndefinedVariable
        if is_message_plugin:
            self.__checkattr(plugin_spec, plugin, 'connectable', bool)
            self.__checkattr(plugin_spec, plugin, 'addcontext', MethodType)
        if is_file_plugin:
            self.__checkattr(plugin_spec, plugin, 'pre_process', MethodType)
        if is_notify_plugin:
            self.__checkattr(plugin_spec, plugin, 'warn', MethodType)

        return plugin

    def __add_last(self, plugin_name):
        if plugin_name in self.plugin_names:
            self.plugin_names.remove(plugin_name)
        self.plugin_names.append(plugin_name)

    def __checkattr(self, plugin_spec, plugin, name, expected_type):
        try:
            attrib = eval('plugin.%s' % name)
        except AttributeError:
            raise PluginError(PLUGIN_ERRORS.missing_attribute, plugin_spec, name) #@UndefinedVariable

        if not isinstance(attrib, expected_type):
            raise PluginError(PLUGIN_ERRORS.invalid_attribute, plugin_spec, name) #@UndefinedVariable


    # with thanks to Ben Snider
    # http://www.bensnider.com/2008/02/27/dynamically-import-and-instantiate-python-classes/
    def __forname(self, module_name, plugin_name):
        ''' Returns a class of "plugin_name" from module "module_name". '''
        __import__(module_name)
        module = sys.modules[module_name]
        classobj = getattr(module, plugin_name)
        return classobj


class Dependency:
    all = list()
    def __init__(self, plugin):
        self.plugin
        self.dep_count = len(plugin.dependencies)

    def map(self, dep_map):
        for spec in self.plugin.dependencies():
            if spec not in dep_map:
                dep_map[spec] = list()
            dep_map[spec].append(self)

    def satisfy(self, plugin, all_plugins):
        self.dep_count -= 1
        if self.dep_count == 0:
            pos = all_plugins.index(plugin)
            all_plugins.insert(pos + 1)
            all.remove(self)


class HotFiles:
    """
    Track the files as they are parsed and manipulated with regards to their git
    status and the dot-control file.
    """
    def __init__(self, project_dir):
        self.project_dir = os.path.realpath(project_dir)
        self.linked_files = dict()
        self.outside_files = set()
        self.control_files = set()
        self.not_exists = set()
        self.to_add = set()
        self.globs = dict()
        self.deleted = set()

    def addfile(self, filename):
        to_expand = os.path.join(self.project_dir, filename)
        file_exists = False
        logging.debug('%s: %s'
               % (filename, glob.glob(to_expand)))
        if sys.hexversion < 0x2050000:
            glob_iter = glob.glob(to_expand)
        else:
            glob_iter = glob.iglob(to_expand)

        pattern = re.compile('(\[.+\]|\*|\?)')
        if pattern.search(filename):
            glob_re = re.sub('\*', '.*', filename)
            glob_re = re.sub('\?', '.', glob_re)
            self.globs[filename] = glob_re

        for expanded_file in glob_iter:
            # track whether iglob iterates at all, if it does not, then the line
            # didn't expand to anything meaningful
            if not file_exists:
                file_exists = True

            # skip the file if some previous glob hit it
            if (expanded_file in self.outside_files
                    or expanded_file in self.linked_files.keys()):
                continue

            # the commit code expects a relative path
            rel_file = self.__make_rel(expanded_file)

            # skip the file if some previous glob hit it
            if rel_file in self.control_files:
                continue

            # checking this after removing the expanded project directory
            # catches absolute paths to files outside the project directory
            if rel_file == expanded_file:
                self.outside_files.add(expanded_file)
                continue

            link = self.__check_link(expanded_file)

            if link == None:
                self.control_files.add(rel_file)
            else:
                self.linked_files[expanded_file] = link

        if not file_exists:
            self.putabsent(filename)

    def contains(self, filename):
        return filename in self.control_files

    def remove(self, filename):
        if filename in  self.control_files:
            self.control_files.remove(filename)

    def putabsent(self, filename):
        self.not_exists.add(filename)

    def putneedsadd(self, filename):
        self.to_add.add(filename)

    def put_deleted(self, filename):
        def __in_target(file_spec):
            return file_spec in self.not_exists
        to_delete = self.from_glob(filename)
        logging.debug('To delete after matching %s' % to_delete)
        to_delete.append(filename)
        to_delete = filter(__in_target, to_delete)
        [self.not_exists.remove(file_spec) for file_spec in to_delete]
        self.deleted.add(filename)

    def from_glob(self, filename):
        """ Returns any original glob-based file specifications from the control file that would match
            the input filename.  Useful for file plugins that add their own globs and need to correlate
            actual files that match their globs. """
        def __match(file_tuple):
            return re.match(file_tuple[1], filename) != None
        matches = filter(__match, self.globs.iteritems())
        matches = dict(matches)
        return matches.keys()

    def warnproblems(self):
        # print warnings for linked files
        for filename in self.linked_files.keys():
            logging.info('%s is a link or its directory path contains a link.' % filename)
        # print warnings for files outside the project
        for filename in self.outside_files:
            logging.info('%s is outside the project directory.' % filename)
        # print warnings for files that do not exists
        for filename in self.not_exists:
            logging.info('%s does not exist.' % filename)
        # print warnings for files that were once under version control but have been deleted
        for filename in self.deleted:
            logging.info('%s has been deleted from version control.' % filename)

    def addorphans(self, git_obj, control_config):
        if len(self.to_add) == 0:
            return

        message_file = flashbake.context.buildmessagefile(control_config)

        to_commit = list()
        for orphan in self.to_add:
            logging.debug('Adding %s.' % orphan)
            add_output = git_obj.add(orphan)
            logging.debug('Add output, %s' % add_output)
            to_commit.append(orphan)

        logging.info('Adding new files, %s.' % to_commit)
        # consolidate the commit to be friendly to how git normally works
        if not control_config.dry_run:
            commit_output = git_obj.commit(message_file, to_commit)
            logging.debug('Commit output, %s' % commit_output)

        os.remove(message_file)

    def needs_warning(self):
        return (len(self.not_exists) > 0
               or len(self.linked_files) > 0
               or len(self.outside_files) > 0
               or len(self.deleted) > 0)

    def __check_link(self, filename):
        # add, above, makes sure filename is always relative
        if os.path.islink(filename):
            return filename
        directory = os.path.dirname(filename)

        while (len(directory) > 0):
            # stop at the project directory, if it is in the path
            if directory == self.project_dir:
                break
            # stop at root, as a safety check though it should not happen
            if directory == os.sep:
                break
            if os.path.islink(directory):
                return directory
            directory = os.path.dirname(directory)
        return None

    def __make_rel(self, filepath):
        return self.__drop_prefix(self.project_dir, filepath)

    def __drop_prefix(self, prefix, filepath):
        if not filepath.startswith(prefix):
            return filepath

        if not prefix.endswith(os.sep):
            prefix += os.sep
        if sys.hexversion < 0x2060000:
            return filepath.replace(prefix, "")
        else:
            return os.path.relpath(filepath, prefix)


def find_executable(executable):
    found = filter(lambda ex: os.path.exists(ex),
                   map(lambda path_token:
                       os.path.join(path_token, executable),
                       os.getenv('PATH').split(os.pathsep)))
    if (len(found) == 0):
        return None
    return found[0]


def executable_available(executable):
    return find_executable(executable) != None
