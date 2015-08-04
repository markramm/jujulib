Hacking on jujulib
==================

Here are some guidelines for hacking on jujulib.

Using a Development Checkout
----------------------------

You'll have to create a development environment to hack on jujulib, using a
jujulib checkout. 

- While logged into your GitHub account, navigate to the jujulib repo on
  GitHub.
  
  https://github.com/juju/jujulib

- Fork and clone the jujulib repository to your GitHub account by clicking
  the "Fork" button.

- Clone your fork of jujulib from your GitHub account to your local computer,
  substituting your account username and specifying the destination as
  "hack-on-jujulib".

   $ cd ~
   $ git clone git@github.com:USERNAME/jujulib.git hack-on-jujulib
   $ cd hack-on-jujulib
   # Configure remotes such that you can pull changes from the jujulib
   # repository into your local repository.
   $ git remote add upstream https://github.com/Pylons/jujulib.git
   # fetch and merge changes from upstream into master
   $ git fetch upstream
   $ git merge upstream/master

Now your local repo is set up such that you will push changes to your GitHub
repo, from which you can submit a pull request.

- Create a virtualenv in which to install jujulib:

   $ cd ~/hack-on-jujulib
   $ virtualenv -ppython2.7 env

  You can choose which Python version you want to use by passing a ``-p``
  flag to ``virtualenv``.  For example, ``virtualenv -ppython2.7``
  chooses the Python 2.7 interpreter to be installed.

  From here on in within these instructions, the ``~/hack-on-jujulib/env``
  virtual environment you created above will be referred to as ``$VENV``.
  To use the instructions in the steps that follow literally, use the
  ``export VENV=~/hack-on-jujulib/env`` command.

- Install ``setuptools-git`` into the virtualenv (for good measure, as we're
  using git to do version control):

   $ $VENV/bin/easy_install setuptools-git

- Install jujulib from the checkout into the virtualenv using ``setup.py
  dev``.  ``setup.py dev`` is an alias for "setup.py develop" which also
  installs testing requirements such as nose and coverage.  Running
  ``setup.py dev`` *must* be done while the current working directory is the
  ``jujulib`` checkout directory:

   $ cd ~/hack-on-jujulib
   $ $VENV/bin/python setup.py dev

- Optionally create a new jujulib project using ``pcreate``:

  $ cd $VENV
  $ bin/pcreate -s starter starter

- ...and install the new project (also using ``setup.py develop``) into the
  virtualenv:

  $ cd $VENV/starter
  $ $VENV/bin/python setup.py develop


Adding Features
---------------

In order to add a feature to jujulib:

- The feature must be documented in both the API and narrative
  documentation (in ``docs/``).

- The feature must work fully on the following CPython versions:
  2.7, 3.2, and 3.3 on both UNIX and Windows.

- The feature must not add dependencies unless previously discussed 
  on the maling list.  Addtional dependencies could block backports
  of jujulib into stable Ubuntu versions. 


Coding Style
------------

- PEP8 compliance.  Whitespace rules are relaxed: not necessary to put
  2 newlines between classes.  But 79-column lines, in particular, are
  mandatory. 

- Please do not remove trailing whitespace.

Running Tests
--------------

- To run all tests for jujulib on a single Python version, run ``nosetests``
  from your development virtualenv (See *Using a Development Checkout* above).

- To run individual tests (i.e. during development) you use ``pytest`` 
  (http://pytest.org/).

   $ $VENV/bin/easy_install pytest
   $ py.test --strict jujulib/

Test Coverage
-------------

- The codebase *must* have 100% test statement coverage after each commit. 

Documentation Coverage and Building HTML Documentation
------------------------------------------------------

If you fix a bug, and the bug requires an API or behavior modification, all
documentation in this package which references that API or behavior must be
changed to reflect the bug fix, ideally in the same commit that fixes the bug
or adds the feature.  To build and review docs, use the following steps.


Change Log
----------

- Feature additions and bugfixes must be added to the ``CHANGES.txt``
  file in the prevailing style.  Changelog entries should be long and
  descriptive, not cryptic.  Other developers should be able to know
  what your changelog entry means.