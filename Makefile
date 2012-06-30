# Makefile or Cloudkick Agent Plugin for supervisord.
#
# Author:: Greg Albrecht <mailto:gba@splunk.com>
# Copyright:: Copyright 2012 Splunk, Inc.
# License:: All rights reserved. Do not redistribute.
#


init:
	pip install -r requirements.txt --use-mirrors

test:
	nosetests tests

lint:
	pylint -i y -r n -f colorized *.py

pep8:
	pep8 *.py

install:
	pip install .

uninstall:
	pip uninstall supervisord_status

develop:
	python setup.py develop

build:
	python setup.py sdist

publish:
	python setup.py sdist upload
