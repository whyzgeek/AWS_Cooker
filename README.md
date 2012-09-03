AWS_Cooker
==========

Is an attemp to create an automated AWS cloud deployment and management system. This is aimed at mid-level scale where you want everything automated but stil want to save on resources by avoiding too much automation. I have put this together based on various examples and codes from here and there. This is only at pilot stage and not meant to be used for production.

## Design

The deployment is majorly based on Amazon Cloudformation. This gives the advantage of managing stacks together rather than dealing with individual resources. Also it makes life easier for rolebacks. However, having all resources defined in one single json, will make it unmaintainable in the long run. Also, you might hit some hard limits that Amazon imposes on these. So I thought to create some sort of way to break down stacks and manage them seperately. This hasn't been implemented yet.

The changes in configurations are managed by two main products. One is puppet and the other is Fabric. It is mainly puppetmaster-less design, relying on repos to check out code. Fabric will be used to do quick manual changes and also running puppet in each instance.


# This is only at proof of concept stage and shouldn't be used for production.
