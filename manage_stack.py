#!/usr/bin/env python
'''
@author: whyzgeek
@contact: whyzgeek@gmail.com
@version: 1.0
@summary: CRUD AWS stacks
'''
__doc__ = """Creates/Reads/Updates/Deletes AWS stacks.
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
import glob
from boto import cloudformation

LOG_MAXBYTE = 100000
LOG_BACKUP_COUNT = 3
LOG_DIR = '/var/log/%s' % APPNAME
LOG_LEVEL = logging.DEBUG
JSON_DIR = '.'
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

class StackManager(object):

    def __init__(self, conn):
        self.conn = conn

    def listStacks(self):
        log.info("Fetching the stack lists and their status")
        return "\n".join([str((x.stack_name, x.stack_status))
                                for x in self.conn.list_stacks()])
    def getStackFile(self, name):
        filename = name.split('-')[0]
        filepath = os.path.normpath("%s/%s.json" % (JSON_DIR, filename))
        return filepath

    def listTempFiles(self):
        return "\n".join(glob.glob(os.path.normpath(
                        "%s/*.json" % JSON_DIR)))

    def listStackRes(self, name):
        return "\n".join((str(x) for x in 
                self.conn.list_stack_resources(name)))

    def createStack(self, name):
        log.info("Fetching the stack %s" % name)
        filepath = self.getStackFile(name)
        log.info("Reading template %s..." % filepath)
        try:
            with open(filepath) as f:
                self.body = f.read()
        except Exception, e:
            log.error("Sorry couldn't read the template %s:%s" % \
                            (filepath, str(e)))
            sys.exit(1)
        try:
            stack = self.conn.create_stack(name, template_body=self.body)
        except boto.exception.BotoServerError, e:
            log.error("Failed to create stack: %s" % e.error_message)
        except Exception, e:
            log.error("Failed to create stack: %s" % str(e))
        else:
            return stack

    def deleteStack(self, name):
        log.info("Deleting stack %s ..." % name)
        try:
            return self.conn.delete_stack(name)
        except Exception, e:
            log.error("Cloudn't delete the stack %s" % str(e))



if __name__ == '__main__':

    if len(sys.argv) == 1:
        print "Specify at least one command. Use --help for help."
        sys.exit(0)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--listStacks', dest='listStacks', action='store_true',
                                           help='Lists all existing stacks and their status.')
    parser.add_argument('--listTemps', dest='listTemps', action='store_true',
                                           help='Lists all existing json templates in %s' % JSON_DIR)
    parser.add_argument('--listStackRes', dest='listStackRes', 
                                           help='Lists all resources associated with a stack')
    parser.add_argument('--create', dest='create',
                                           help='Creates a stack with a name. Name must start with json template name.'
                                           'dashes can be used after that to specify environment or other properties.')
    parser.add_argument('--delete', dest='delete',
                                           help='Deletes the named stack specified.')
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
    try:
        conn = cloudformation.connection.CloudFormationConnection(aws_access_key_id = args.aws_access_key_id, 
                               aws_secret_access_key = args.aws_secret_access_key)
    except Exception, e:
        log.error("Failed to connect to cloud formation %s" % str(e))
    manager = StackManager(conn)
    if args.listStacks:
        print manager.listStacks()
    elif args.listTemps:
        print manager.listTempFiles()
    elif args.listStackRes:
        print manager.listStackRes(args.listStackRes)
    elif args.create:
        log.info("Initiated %s" %  manager.createStack(args.create))
    elif args.delete:
        print manager.deleteStack(args.delete)
        log.info("Delete success.")

    log.info("FINISHED running %s" % __file__)
