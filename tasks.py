import os
import logging

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from wsgiref.simple_server import make_server

logging.basicConfig()
log = logging.getLogger(__file__)

here = os.path.dirname(os.path.abspath(__file__))


