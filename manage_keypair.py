#!/usr/bin/env python
'''
@author: whyzgeek
@contact: whyzgeek@gmail.com
@version: 1.0
@summary: CRUD AWS EC2 key pairs
'''
__doc__ = """Creates/Reads/Updates/Deletes AWS EC2 Key pairs. These are used to SSH access instances.
"""
VERSION = '1.0'
APPNAME = 'AWS_Cooker'
FILENAME = __file__.split('/')[-1][:-3]
import os
import logging
import logging.handlers
import commands
import shutil
import sys
import argparse
import json
import grp
import pwd
import boto

LOG_MAXBYTE = 100000
LOG_BACKUP_COUNT = 3
LOG_DIR = '/var/log/%s' % APPNAME
LOG_LEVEL = logging.DEBUG
log = None

def setup_logging(logdir=LOG_DIR, scrnlog=True, txtlog=True, loglevel=LOG_LEVEL):
    global log
    logdir = os.path.abspath(logdir)

    log = logging.getLogger(FILENAME)
    log.setLevel(loglevel)

    log_formatter = logging.Formatter("%(asctime)s - %(name)s - "
                                    "%(levelname)s - %(message)s")

    if txtlog:
        if not os.path.exists(logdir):
            try:
                os.mkdir(logdir)
            except OSError, e:
                print "Couldn't create log file dir %s" % logdir
                print str(e)
                sys.exit(1)

        txt_handler = logging.handlers.RotatingFileHandler(
                            os.path.join(logdir, "%s.log" % FILENAME),
                            maxBytes=LOG_MAXBYTE, backupCount=LOG_BACKUP_COUNT)
        txt_handler.doRollover()
        txt_handler.setFormatter(log_formatter)
        try:
            log.addHandler(txt_handler)
            log.info("STARTED! Logfile opened for writing...")
        except Exception, e:
            print "Logfile %s.log couldn't be created because %s" % \
                                        (FILENAME, str(e))

    if scrnlog:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        log.addHandler(console_handler)
    return log

class KeyPairManager(object):

    def __init__(self, ec2conn):
        self.ec2conn = ec2conn

    def getAllKeyPairs(self):
        return self.ec2conn.get_all_key_pairs()

    def createKeyPair(self, name):
        log.info('Creating a new RSA key/pair with name %s' % name)
        return self.ec2conn.create_key_pair(name)

    def getKeyPair(self, name):
        return self.ec2conn.get_key_pair(name)

    def savePEMKey(self, name, keyPair):
        log.info('Saving private key to %s.pem' % name)
        success = keyPair.save(os.path.expanduser('~'))
        if success:
            log.info('Successfully saved the pem file.')
        else:
            log.error('Failed to save the pem file.')
            sys.exit(1)
    def createAndSavePEM(self, name):
        kp = self.createKeyPair(name)
        self.savePEMKey(name, kp)

    def deleteKeyPair(self, name):
        log.info('Deleting the key %s' % name)
        self.ec2conn.delete_key_pair(name)


if __name__ == '__main__':

    if len(sys.argv) == 1:
        print "Specify at least one command. Use --help for help."
        sys.exit(0)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list', dest='list', action='store_true',
                                           help='Lists all existing keypairs.')
    parser.add_argument('--create', dest='create',
                                           help='Creates a key/pair and store it with the name specified, '
                                           'and  save it in ~/.ssh')
    parser.add_argument('--delete', dest='delete',
                                           help='Delete a key/pair with the name specified.')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                                           help='Turns on debug mode.')
    parser.add_argument('--noscreen', dest='noscreen', action='store_false',
                                           help='Turns off screen logging')
    parser.add_argument('--logdir', dest='logdir', default=LOG_DIR,
           help='Log file path. Default: %s' % LOG_DIR)
    parser.add_argument('--aws_access_key_id', dest='aws_access_key_id', default=None,
            help='aws_access_key_id, either specify here or in /etc/boto.cfg'
            ' or AWS_ACCESS_KEY_ID environment var.')
    parser.add_argument('--aws_secret_access_key', dest='aws_secret_access_key', default=None,
            help='aws_secret_access_key, either specify here or in /etc/boto.cfg'
            ' or AWS_SECRET_ACCESS_KEY environment var.')
    parser.add_argument('--version', action='version', version='%s %s' % (__file__, VERSION))

    args = parser.parse_args()
    LOG_DIR = args.logdir

    if args.verbose:
        LOG_LEVEL = logging.DEBUG

    log = setup_logging()

    ec2conn = boto.connect_ec2(aws_access_key_id = args.aws_access_key_id, 
                               aws_secret_access_key = args.aws_secret_access_key)
    manager = KeyPairManager(ec2conn)
    if args.list:
        print manager.getAllKeyPairs()
    elif args.create:
        manager.createAndSavePEM(args.create)
        print "use ssh -i ~/% <root|ubuntu>@<instance> to connect to each instance."
    elif args.delete:
        manager.deleteKeyPair(args.delete)
        print "Delete success."

    log.info("FINISHED running %s" % __file__)
