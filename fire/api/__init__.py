class ObjectNotFound(Exception):
    pass

from . import server

app = server.app
db = server.db

from . import controllers

controllers.add_routes(app)

db.create_all()
