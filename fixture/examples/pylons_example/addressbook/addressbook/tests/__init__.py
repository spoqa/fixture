"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import config, url
from routes.util import URLGenerator
from webtest import TestApp

# additional imports ...
from paste.deploy import appconfig
from addressbook.config.environment import load_environment

import pylons.test

# export dbfixture here for tests :
__all__ = ['environ', 'url', 'TestController', 'dbfixture']

# Invoke websetup with the current config file
##### comment this out so that initial data isn't loaded:
# SetupCommand('setup-app').run([config['__file__']])

##### but add this so that your models get configured:
appconf = appconfig('config:' + config['__file__'])
load_environment(appconf.global_conf, appconf.local_conf)

environ = {}

from addressbook import model
from addressbook.model import meta
from fixture import SQLAlchemyFixture
from fixture.style import NamedDataStyle

dbfixture = SQLAlchemyFixture(
    env=model,
    engine=meta.engine,
    style=NamedDataStyle()
)

def setup():
    meta.metadata.create_all(meta.engine)

def teardown():
    meta.metadata.drop_all(meta.engine)

class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        if pylons.test.pylonsapp:
            wsgiapp = pylons.test.pylonsapp
        else:
            wsgiapp = loadapp('config:%s' % config['__file__'])
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)
        
    def setUp(self):
        # remove the session once per test so that 
        # objects do not leak from test to test
        meta.Session.remove()
