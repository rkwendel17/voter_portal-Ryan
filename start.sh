#!/bin/zsh

export APPLICATION_SETTINGS=config_dev.py

export FLASK_APP=app
export FLASK_ENV=development
flask run -p 8000
