'''
Created on Jul 23, 2009

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
from flashbake import plugins
import logging
import os
import smtplib
import sys


# Import the email modules we'll need
if sys.hexversion < 0x2050000:
    from email.MIMEText import MIMEText
else:
    from email.mime.text import MIMEText


class Email(plugins.AbstractNotifyPlugin):
    def notify(self, hot_files, control_config):
        body = ''
        
        if len(hot_files.not_exists) > 0:
            body += '\nThe following files do not exist:\n\n'
    
            for file in hot_files.not_exists:
               body += '\t' + file + '\n'
    
            body += '\nMake sure there is not a typo in .flashbake and that you created/saved the file.\n'
        
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
    
    
        if control_config.dryrun:
            logging.debug(body)
            if control_config.notice_to != None:
                logging.info('Dry run, skipping email notice.')
            return
    
        # Create a text/plain message
        msg = MIMEText(body, 'plain')
    
        msg['Subject'] = ('Some files in %s do not exist'
                % os.path.realpath(hot_files.project_dir))
        msg['From'] = control_config.notice_from
        msg['To'] = control_config.notice_to
    
        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        logging.debug('\nConnecting to SMTP on host %s, port %d'
                % (control_config.smtp_host, control_config.smtp_port))
    
        try:
            s = smtplib.SMTP()
            s.connect(host=control_config.smtp_host,port=control_config.smtp_port)
            logging.info('Sending notice to %s.' % control_config.notice_to)
            logging.debug(body)
            s.sendmail(control_config.notice_from, [control_config.notice_to], msg.as_string())
            logging.info('Notice sent.')
            s.close()
        except Exception, e:
            logging.error('Couldn\'t connect, will send later.')
            logging.debug("SMTP Error:\n" + str(e));
