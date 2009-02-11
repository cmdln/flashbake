#
#  timezone.py
#  Stock plugin to find the system's time zone add to the commit message.

from flashbake.context import findtimezone

connectable = False

def addcontext(message_file, control_config):
    """ Add the system's time zone to the commit context. """

    zone = findtimezone()

    if zone == None:
        message_file.write('Couldn\'t determine time zone.\n')
    else:
        message_file.write('Current time zone is %s\n' % zone)

    return True
