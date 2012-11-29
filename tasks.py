import os
import logging

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.events import NewRequest
from pyramid.events import subscriber
from pyramid.events import ApplicationCreated
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

import sqlite3

from wsgiref.simple_server import make_server

logging.basicConfig()
log = logging.getLogger(__file__)

here = os.path.dirname(os.path.abspath(__file__))


@view_config(route_name='list', renderer='list.mako')
def list_view(request):
    rs = request.db.execute("select id, name from tasks where closed = 0")
    tasks = [dict(id=row[0], name=row[1]) for row in rs.fetchall()]
    return {'tasks': tasks}

@subscriber(ApplicationCreated)
def application_created_subscriber(event):
    log.warn('Initializing database...')
    f = open(os.path.join(here, 'schema.sql'), 'r')
    stmt = f.read()
    settings = event.app.registry.settings
    db = sqlite3.connect(settings['db'])
    db.executescript(stmt)
    db.commit()
    f.close()

@subscriber(NewRequest)
def new_request_subscriber(event):
    request = event.request
    settings = request.registry.settings
    request.db = sqlite3.connect(settings['db'])
    request.add_finished_callback(close_db_connection)

def close_db_connection(request):
    request.db.close()


if __name__ == '__main__':
    # configuration settings
    settings = {}
    settings['reload_all'] = True
    settings['debug_all'] = True
    settings['db'] = os.path.join(here, 'tasks.db')
    # session factory
    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    # configuration setup
    config = Configurator(settings=settings, session_factory=session_factory)
    # scan for @view_config and @subscriber decorators
    config.scan()
    # serve app
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
