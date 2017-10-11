#!/usr/bin/env python
import os

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import make_response, jsonify

import click

import fire
fire.load_config(os.getenv("CONFIG_FILE"))

from fire import config
from fire.api import ObjectNotFound

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.get(["general", "database"])
app.config['ERROR_404_HELP'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

def error(status_code, message):
    return make_response(jsonify(dict(status="error", message=message)), status_code)

@app.errorhandler(404)
def page_not_found(exception):
    return error(404, "The requested URL was not found on the server")

@app.errorhandler(ObjectNotFound)
def object_not_found(exception):
    return error(404, "Object not found: {}".format(str(exception)))

@app.cli.command()
def seed():
    """Initialize the db with seed data."""
    from fire.api import seeds
    seeds.run()
    click.echo('Done')
