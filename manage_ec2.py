#!/usr/bin/env python
'''
@author: whyzgeek
@contact: whyzgeek@gmail.com
@version: 1.0
@summary: Manages EC2 instances
'''
__doc__ = """Manages EC2 instances
"""
VERSION = '1.0'
import os
import logging
import logging.handlers
import sys
import argparse
import json
import boto
from fabric import api as fabapi
from utils import *

SSH_USER = 'ubuntu'
DEPLOY_KEY = '~/deploy.pem'
PUPPET_CONFIG_PATH = '/etc/puppet/manifests/init.pp'
PUPPET_ROOT = '/etc/puppet'
fabapi.env['key_filename'] = DEPLOY_KEY
fabapi.env['user'] = SSH_USER
cmd = None

@fabapi.task
def fabSudoTask():
    fabapi.sudo(cmd)


class EC2Manager(object):

    def __init__(self, ec2conn):
        self.ec2conn = ec2conn

    def getAllInstances(self):
        instances = []
        for y in [x.instances for \
                                x in self.ec2conn.get_all_instances()]:
            instances.extend(y)
        return instances

    def getAllInstancesStr(self):
        return "\n".join([str([x.dns_name, x.id, \
                x.image_id, x.ip_address, x.region]) \
                for x in self.getAllInstances()])

    def getAllStackInstances(self, stackname):
        instances = []
        filters = { 'tag:aws:cloudformation:stack-name' : stackname }
        for y in [x.instances for \
                                x in self.ec2conn.get_all_instances()]:
            instances.extend(y)
        return instances

    def getAllStackInstancesStr(self, stackname):
        return "\n".join([str([x.dns_name, x.id, \
                x.image_id, x.ip_address, x.region, stackname]) \
                for x in self.getAllInstances()])

    def populateEnvHosts(self, stackname):
        if not fabapi.env['hosts']:
            fabapi.env['hosts'] = [ x.dns_name for x in \
                            self.getAllStackInstances(stackname)]

    def runGitPullOnStack(self, stackname):
        global cmd
        self.populateEnvHosts(stackname)
        cmd = 'cd %s && git pull' % PUPPET_ROOT
        log.info("Running %s on %s" % (cmd, fabapi.env['hosts']))
        output = fabapi.execute(fabSudoTask, hosts=fabapi.env['hosts'])
        return output

    def runPuppetApplyOnStack(self, stackname):
        global cmd
        self.runGitPullOnStack(stackname)
        cmd = 'puppet apply -v %s' % PUPPET_CONFIG_PATH
        log.info("Running %s on %s" % (cmd, fabapi.env['hosts']))
        output = fabapi.execute(fabSudoTask, hosts=fabapi.env['hosts'])
        return output


if __name__ == '__main__':

    if len(sys.argv) == 1:
        print "Specify at least one command. Use --help for help."
        sys.exit(0)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--listAll', dest='listAll', action='store_true',
                                           help='Lists all EC2 instances.')
    parser.add_argument('--listStack', dest='listStack',
                                           help='Lists all EC2 instances associated with'
                                           'specified stack')
    parser.add_argument('--puppetApplyStack', dest='puppetApplyStack',
                                           help='Syncs puppet configs and apply them'
                                           'on all instances on specified stack')
    parser.add_argument('--create', dest='create',
                                           help='Not implemented')
    parser.add_argument('--delete', dest='delete',
                                           help='Not implemented')
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
    manager = EC2Manager(ec2conn)
    if args.listAll:
        print manager.getAllInstancesStr()
    elif args.listStack:
        print manager.getAllStackInstancesStr(args.listStack)
    elif args.puppetApplyStack:
        manager.runPuppetApplyOnStack(args.puppetApplyStack)

    log.info("FINISHED running %s" % __file__)
