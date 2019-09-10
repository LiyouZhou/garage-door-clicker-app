#!/usr/bin/env python3

from flask import Flask
from invoke_click import env_loader
from threading import Lock

app = Flask(__name__)

clicker_lock = Lock()

@app.route('/open/sesame')
def hello_world():
    with clicker_lock:
        env_loader()
    return 'Opened'
