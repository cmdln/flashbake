#
#  context.py
#  Build up some descriptive context for automatic commit to git

import sys
import os
import os.path
import string
import random
import logging

def buildmessagefile(config):
    """ Build a commit message that uses the provided ControlConfig object and
        return a reference to the resulting file. """
    config.init()

    msg_filename = '/tmp/git_msg_%d' % random.randint(0,1000)

    # try to avoid clobbering another process running this script
    while os.path.exists(msg_filename):
        msg_filename = '/tmp/git_msg_%d' % random.randint(0,1000)

    connectable = False
    connected = False

    message_file = open(msg_filename, 'w')
    try:
        for plugin in config.msg_plugins:
            plugin_success = plugin.addcontext(message_file, config)
            # let each plugin say which ones attempt network connections
            if plugin.connectable:
                connectable = True
                connected = connected or plugin_success
        if connectable and not connected:
            message_file.write('All of the plugins that use the network failed.\n')
            message_file.write('Your computer may not be connected to the network.')
    finally:
        message_file.close()
    return msg_filename
