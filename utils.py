#!/usr/bin/env python
'''
@author: whyzgeek
@contact: whyzgeek@gmail.com
@version: 1.0
@summary: Utility library for shared functions
'''
__doc__ = """Utility library for shared functions
"""
APPNAME = 'AWS_Cooker'
FILENAME = __file__.split('/')[-1][:-3]
import os
import logging
import logging.handlers
import argparse
import sys

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



