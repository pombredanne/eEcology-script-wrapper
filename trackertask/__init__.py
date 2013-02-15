from pyramid.config import Configurator
from sqlalchemy import engine_from_config

#from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
#    engine = engine_from_config(settings, 'sqlalchemy.')
#    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)

    config.add_route('index', '/')
    config.add_route('apply', '/apply/{script}')
    config.add_route('status', '/status/{script}/{taskid}')
    config.add_route('result', '/result/{script}/{taskid}')

    config.scan()

    return config.make_wsgi_app()
