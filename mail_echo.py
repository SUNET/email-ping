#!/path/to/python2.7
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 10:31:41 2011

@author: lundberg
"""
import sys
import logging
import email
from email.mime.text import MIMEText
import smtplib

# Settings
smtp_server = '<SUBMISSION_SERVER>:587'
smtp_debug_level = 1
username = '<USERNAME>'
password = '<PASSPHRASE>'
#echo_from = 'echo@SUNET.SE <echo-reply@sunet.se>'
echo_from = 'echo-reply@sunet.se'
custom_msg = '''
ECHO Server at sunet.se received your message with the following header:
'''
signature = 'Postmaster'

# Set up logging
logger = logging.getLogger('mail_echo')
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh = logging.StreamHandler([sys.stdout])
sh.setFormatter(formatter)
logger.addHandler(sh)

def send_msg(msg):
    '''
    Takes an e-mail message and send it via the configured SMTP server.
    '''
    try:
        server = smtplib.SMTP(smtp_server)
        server.set_debuglevel(smtp_debug_level)
        if username:
            server.starttls()  
            server.login(username, password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
    except Exception as e:
        logger.error(e)

def get_email_message(m):
    '''
    Takes an e-mail as a string and returns an email.message.Message().
    '''
    try:
        if type(m).__name__ == 'file':
            msg = email.message_from_file(m)
        else:
            msg = email.message_from_string(m)
    except email.errors.MessageError as e:
        logger.error(e)
    return msg

def echo_mail(msg):
    '''
    Takes an e-mail message and extracts the headers, from, subject and date 
    then returns this information to the sender.
    '''
    reply_body = 'Your Date line was Date:\t%s\n' % msg.get('Date')
    reply_body += 'Now is:\t\t\t\t\t%s\n' % email.utils.formatdate(localtime=True)
    reply_body += '\n%s\n\n' % custom_msg
    reply_body += '\t-------  Original Header -------\n\n'
    for header in msg.get_all('Received'):
        reply_body += 'Received: %s\n' % header
    reply_body += '\n\t-------   End of Header  -------\n\n'
    reply_body += '%s' % signature
    reply = MIMEText(reply_body)
    reply['To'] = msg.get('From')
    reply['Cc'] = msg.get('Cc')
    reply['Subject'] = 'Re: %s' % msg.get('Subject') 
    reply['From'] = echo_from
    send_msg(reply)

def main():
    try:
        # Open stdin for reading if no files where provided.
        if len(sys.argv) == 1:
            f = sys.stdin
            msg = get_email_message(f)
            echo_mail(msg)
        else:
            # Open files provided as arguments.
            for f in sys.argv[1:]:
                f = open(f)
                msg = get_email_message(f)
                echo_mail(msg)
    except Exception as e:
        logger.error(e)
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()
