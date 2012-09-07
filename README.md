AWS_Cooker
==========

It is an attempt to create an automated AWS cloud deployment and management system. This is aimed at mid-level scale where you want everything automated but still want to save on resources. I have put this together based on various examples and codes from here and there. This is only at pilot stage and not meant to be used for production.

## Design

The deployment is majorly based on Amazon Cloudformation. This gives the advantage of managing stacks together rather than dealing with individual resources. Also it makes life easier for rollbacks. However, having all resources defined in one single json, will make it unmaintainable in the long run. Also, you might hit some hard limits that Amazon imposes on these. So I thought to create some sort of way to break down stacks and manage them separately. This hasn't been implemented yet.

Two main tools manage the changes in configurations. One is puppet and the other is Fabric. It is mainly puppetmaster-less design, relying on repos to check out code. Fabric will be used to do quick manual changes and also running puppet in each instance.


# This is only at proof of concept stage and shouldn't be used for production.

Some usages:
```
mypc:AWS_Cooker me$ export AWS_ACCESS_KEY_ID="XXXXXXXXXXXXXX"
mypc:AWS_Cooker me$ export AWS_SECRET_ACCESS_KEY="XXXXXXXXXXXXX"
mypc:AWS_Cooker me$ ./manage_stack.py --create autoscalingWeb-Test
2012-09-04 09:03:34,547 - manage_stack - INFO - Fetching the stack autoscalingWeb-Test
2012-09-04 09:03:34,548 - manage_stack - INFO - Reading template autoscalingWeb.json...
2012-09-04 09:03:42,575 - manage_stack - INFO - Initiated arn:aws:cloudformation:us-east-1:082298858524:stack/autoscalingWeb-Test/0b1b2be0-f667-11e1-b6dc-5081c372a74e
2012-09-04 09:03:42,575 - manage_stack - INFO - FINISHED running ./manage_stack.py
mypc:AWS_Cooker me$ ./manage_stack.py --listStacks
2012-09-04 09:05:41,217 - manage_stack - INFO - Fetching the stack lists and their status
(u'autoscalingWeb-Test', u'CREATE_IN_PROGRESS')
mypc:AWS_Cooker me$ ./manage_ec2.py --puppet autoscalingWeb-Test
2012-09-04 14:39:44,521 - utils. - INFO - Running cd /etc/puppet && git pull on [u'ec2-50-16-142-192.compute-1.amazonaws.com', u'ec2-184-73-5-243.compute-1.amazonaws.com']
[ec2-50-16-142-192.compute-1.amazonaws.com] Executing task 'fabSudoTask'
[ec2-50-16-142-192.compute-1.amazonaws.com] sudo: cd /etc/puppet && git pull
[ec2-50-16-142-192.compute-1.amazonaws.com] out: Already up-to-date.

[ec2-184-73-5-243.compute-1.amazonaws.com] Executing task 'fabSudoTask'
[ec2-184-73-5-243.compute-1.amazonaws.com] sudo: cd /etc/puppet && git pull
[ec2-184-73-5-243.compute-1.amazonaws.com] out: remote: Counting objects: 9, done.
[ec2-184-73-5-243.compute-1.amazonaws.com] out: remote: Compressing objects: 100% (1/1), done.
[ec2-184-73-5-243.compute-1.amazonaws.com] out: remote: Total 5 (delta 2), reused 5 (delta 2)
[ec2-184-73-5-243.compute-1.amazonaws.com] out: Unpacking objects: 100% (5/5), done.
[ec2-184-73-5-243.compute-1.amazonaws.com] out: From https://github.com/whyzgeek/AWS_Cooker_Puppet
[ec2-184-73-5-243.compute-1.amazonaws.com] out:    f0b7605..bbaa3d7  master     -> origin/master
[ec2-184-73-5-243.compute-1.amazonaws.com] out: Updating f0b7605..bbaa3d7
[ec2-184-73-5-243.compute-1.amazonaws.com] out: Fast-forward
[ec2-184-73-5-243.compute-1.amazonaws.com] out:  private/www/index.html |    4 ++--
[ec2-184-73-5-243.compute-1.amazonaws.com] out:  1 files changed, 2 insertions(+), 2 deletions(-)

2012-09-04 14:39:52,906 - utils. - INFO - Running puppet apply -v /etc/puppet/manifests/init.pp on [u'ec2-50-16-142-192.compute-1.amazonaws.com', u'ec2-184-73-5-243.compute-1.amazonaws.com']
[ec2-50-16-142-192.compute-1.amazonaws.com] Executing task 'fabSudoTask'
[ec2-50-16-142-192.compute-1.amazonaws.com] sudo: puppet apply -v /etc/puppet/manifests/init.pp
[ec2-50-16-142-192.compute-1.amazonaws.com] out: info: Applying configuration version '1346765986'
[ec2-50-16-142-192.compute-1.amazonaws.com] out: info: FileBucket adding {md5}4ecd3a77ef8ac3c285460b11765abaac
[ec2-50-16-142-192.compute-1.amazonaws.com] out: info: /File[/var/www/index.html]: Filebucketed /var/www/index.html to puppet with sum 4ecd3a77ef8ac3c285460b11765abaac
[ec2-50-16-142-192.compute-1.amazonaws.com] out: notice: /File[/var/www/index.html]/content: content changed '{md5}4ecd3a77ef8ac3c285460b11765abaac' to '{md5}377f7396ee60e38e1a45c9af31e31a7f'
[ec2-50-16-142-192.compute-1.amazonaws.com] out: notice: Finished catalog run in 0.19 seconds

[ec2-184-73-5-243.compute-1.amazonaws.com] Executing task 'fabSudoTask'
[ec2-184-73-5-243.compute-1.amazonaws.com] sudo: puppet apply -v /etc/puppet/manifests/init.pp
[ec2-184-73-5-243.compute-1.amazonaws.com] out: info: Applying configuration version '1346765992'
[ec2-184-73-5-243.compute-1.amazonaws.com] out: info: FileBucket adding {md5}4ecd3a77ef8ac3c285460b11765abaac
[ec2-184-73-5-243.compute-1.amazonaws.com] out: info: /File[/var/www/index.html]: Filebucketed /var/www/index.html to puppet with sum 4ecd3a77ef8ac3c285460b11765abaac
[ec2-184-73-5-243.compute-1.amazonaws.com] out: notice: /File[/var/www/index.html]/content: content changed '{md5}4ecd3a77ef8ac3c285460b11765abaac' to '{md5}377f7396ee60e38e1a45c9af31e31a7f'
[ec2-184-73-5-243.compute-1.amazonaws.com] out: notice: Finished catalog run in 0.25 seconds

2012-09-04 14:40:00,794 - utils. - INFO - FINISHED running ./manage_ec2.py
mypc:AWS_Cooker me$ ./manage_stack.py --delete autoscalingWeb-Test
2012-09-04 14:50:39,022 - utils. - INFO - Deleting stack autoscalingWeb-Test ...
{u'DeleteStackResponse': {u'ResponseMetadata': {u'RequestId': u'7e0ab158-f697-11e1-b774-094b9d1bd52c'}}}
2012-09-04 14:50:40,833 - utils. - INFO - Delete success.
2012-09-04 14:50:40,834 - utils. - INFO - FINISHED running ./manage_stack.py
```
