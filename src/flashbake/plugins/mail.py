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

'''
Created on Jul 23, 2009

mail.py - plug-in to send notices via smtp.

@author: cmdln
'''

from flashbake import plugins
import logging
import os
import smtplib
import sys


# Import the email modules we'll need
if sys.hexversion < 0x2050000:
    from email.MIMEText import MIMEText #@UnusedImport
else:
    from email.mime.text import MIMEText #@Reimport



class Email(plugins.AbstractNotifyPlugin):
    def __init__(self, plugin_spec):
        plugins.AbstractPlugin.__init__(self, plugin_spec)
        self.define_property('notice_to', required=True)
        self.define_property('notice_from')
        self.define_property('smtp_host', default='localhost')
        self.define_property('smtp_port', int, default=25)

    def init(self, config):
        if self.notice_from == None:
            self.notice_from = self.notice_to

    def warn(self, hot_files, control_config):
        body = ''

        if len(hot_files.not_exists) > 0:
            body += '\nThe following files do not exist:\n\n'

            for file in hot_files.not_exists:
                body += '\t' + file + '\n'

            body += '\nMake sure there is not a typo in .flashbake and that you created/saved the file.\n'

        if len(hot_files.deleted) > 0:
            body += '\nThe following files have been deleted from version control:\n\n'

            for file in hot_files.deleted:
                body += '\t' + file + '\n'

            body += '\nYou may restore these files or remove them from .flashbake after running flashbake --purge '
            body += 'in your project directory.\n'

        if len(hot_files.linked_files) > 0:
            body += '\nThe following files in .flashbake are links or have a link in their directory path.\n\n'

            for (file, link) in hot_files.linked_files.iteritems():
                if file == link:
                    body += '\t' + file + ' is a link\n'
                else:
                    body += '\t' + link + ' is a link on the way to ' + file + '\n'

            body += '\nMake sure the physical file and its parent directories reside in the project directory.\n'

        if len(hot_files.outside_files) > 0:
            body += '\nThe following files in .flashbake are not in the project directory.\n\n'

            for file in hot_files.outside_files:
                body += '\t' + file + '\n'

            body += '\nOnly files in the project directory can be tracked and committed.\n'


        if control_config.dry_run:
            logging.debug(body)
            if self.notice_to != None:
                logging.info('Dry run, skipping email notice.')
            return

        # Create a text/plain message
        msg = MIMEText(body, 'plain')

        msg['Subject'] = ('Some files in %s do not exist'
                % os.path.realpath(hot_files.project_dir))
        msg['From'] = self.notice_from
        msg['To'] = self.notice_to

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        logging.debug('\nConnecting to SMTP on host %s, port %d'
                % (self.smtp_host, self.smtp_port))

        try:
            s = smtplib.SMTP()
            s.connect(host=self.smtp_host, port=self.smtp_port)
            logging.info('Sending notice to %s.' % self.notice_to)
            logging.debug(body)
            s.sendmail(self.notice_from, [self.notice_to], msg.as_string())
            logging.info('Notice sent.')
            s.close()
        except Exception, e:
            logging.error('Couldn\'t connect, will send later.')
            logging.debug("SMTP Error:\n" + str(e));
