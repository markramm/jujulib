# jujulib
Python juju client library

Juju is a modern tool for modeling, deploying and managing software services.  It was designed to help tool developers, application developers, and operations team to reason and collaborate effectively about sets of machines, services, service-units, and all of the infrastructure needed to run a modern application. 

Jujulib is a python library designed to automate Juju.  It is intended to be used to provide higher level orchestration of juju.  It can be used to bootstrap a juju server, setup environments, deploy services, connect (or in juju's terms *relate*) services. 

> A key design goal for jujulib is to allow python developers to create complex
> topologies of services quickly and easily, and to automate  logic about how 
> to manage, scale, and test services.  

We expect jujulib, jujuci, and test actions on various charms to work together to make it possible to do complex integration tests with just a few lines of python code. 
